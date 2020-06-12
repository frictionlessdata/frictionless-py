# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six
import datetime
import operator
import tabulator
import tableschema
from . import cells
from copy import copy
from multiprocessing.pool import ThreadPool
from .registry import registry
from .error import Error
from . import exceptions
from . import config


# Module API


class Inspector(object):

    # Public

    def __init__(
        self,
        checks=['structure', 'schema'],
        skip_checks=[],
        infer_schema=False,
        infer_fields=False,
        order_fields=False,
        error_limit=config.DEFAULT_ERROR_LIMIT,
        table_limit=config.DEFAULT_TABLE_LIMIT,
        row_limit=config.DEFAULT_ROW_LIMIT,
    ):

        # Set attributes
        self.__checks = checks
        self.__skip_checks = skip_checks
        self.__infer_schema = infer_schema
        self.__infer_fields = infer_fields
        self.__order_fields = order_fields

        parse_limit = lambda num: float('inf') if (num < 0) else num  # noqa:E731
        self.__error_limit = parse_limit(error_limit)
        self.__table_limit = parse_limit(table_limit)
        self.__row_limit = parse_limit(row_limit)

    def inspect(self, source, preset=None, **options):

        # Start timer
        start = datetime.datetime.now()

        # Prepare preset
        preset = self.__get_source_preset(source, preset)
        if preset == 'nested':
            options['presets'] = self.__presets
            for s in source:
                if s.get('preset') is None:
                    s['preset'] = self.__get_source_preset(s['source'])

        # Prepare tables
        preset_func = self.__get_preset(preset)['func']
        warnings, tables = preset_func(source, **options)
        if len(tables) > self.__table_limit:
            warnings.append(
                'Dataset inspection has reached %s table(s) limit' % (self.__table_limit)
            )
            tables = tables[: self.__table_limit]

        # Collect table reports
        table_reports = []
        if tables:
            tasks = []
            pool = ThreadPool(processes=len(tables))
            try:
                for table in tables:
                    tasks.append(pool.apply_async(self.__inspect_table, (table,)))
                for task in tasks:
                    table_warnings, table_report = task.get()
                    warnings.extend(table_warnings)
                    table_reports.append(table_report)
            finally:
                pool.terminate()

        # Stop timer
        stop = datetime.datetime.now()

        # Compose report
        report = {
            'time': round((stop - start).total_seconds(), 3),
            'valid': all(item['valid'] for item in table_reports),
            'error-count': sum(len(item['errors']) for item in table_reports),
            'table-count': len(tables),
            'tables': table_reports,
            'warnings': warnings,
            'preset': preset,
        }

        return report

    # Internal

    @property
    def __presets(self):
        return registry.compile_presets()

    def __get_preset(self, preset):
        try:
            return self.__presets[preset]
        except KeyError:
            message = 'Preset "%s" is not registered' % preset
            raise exceptions.GoodtablesException(message)

    def __get_source_preset(self, source, preset=None):
        if preset is None:
            preset = 'table'
            if isinstance(source, six.string_types):
                source_path = source.lower()
                if source_path.endswith('datapackage.json') or source_path.endswith(
                    '.zip'
                ):
                    preset = 'datapackage'
            elif isinstance(source, dict):
                if 'resources' in source:
                    preset = 'datapackage'
            elif isinstance(source, list):
                if source and isinstance(source[0], dict) and 'source' in source[0]:
                    preset = 'nested'

        return preset

    def __infer(self, sample, headers=None):
        if headers is None:
            headers = [None] * len(sample[0]) if sample else []
        schema = tableschema.Schema()
        schema.infer(sample, headers=headers)
        return schema

    def __inspect_table(self, table):

        # Start timer
        start = datetime.datetime.now()

        # Prepare vars
        errors = []
        warnings = []
        headers = []
        row_number = 0
        fatal_error = False
        source = table['source']
        stream = table['stream']
        schema = table['schema']
        extra = table['extra']

        # Prepare checks
        checks = registry.compile_checks(
            table.get('checks', self.__checks),
            self.__skip_checks,
            order_fields=self.__order_fields,
            infer_fields=self.__infer_fields,
        )

        # Prepare table
        try:
            stream.open()
            sample = stream.sample
            headers = stream.headers
            if headers is None:
                headers = [None] * len(sample[0]) if sample else []
            if _filter_checks(checks, type='schema'):
                if schema is None and self.__infer_schema:
                    schema = self.__infer(sample, headers)
            if schema is None:
                checks = _filter_checks(checks, type='schema', inverse=True)
        except Exception as exception:
            error, fatal_error = _compose_error_from_exception(exception)
            errors.append(error)

        # Prepare schema
        if not fatal_error:
            if schema:
                if schema.primary_key:
                    for field in schema.descriptor.get('fields', []):
                        if field.get('name') in schema.primary_key:
                            field['primaryKey'] = True
                    schema.commit()
                for error in schema.errors:
                    fatal_error = True
                    error = _compose_error_from_schema_error(error)
                    errors.append(error)

        # Prepare checks
        # This is an experimental hook
        for check in checks:
            prepare_func = getattr(check['func'], 'prepare', None)
            if not prepare_func:
                continue
            success = prepare_func(stream, schema, extra)
            if not success:
                checks.remove(check)
        if not checks:
            fatal_error = True

        # Head checks
        if not fatal_error:
            # Prepare cells
            fields = [None] * len(headers)
            if schema is not None:
                fields = schema.fields
            header_cells = cells.create_cells(headers, fields)

            # Fix for issue 312
            has_headers = headers is not None
            if has_headers:
                head_checks = _filter_checks(checks, context='head')
                for check in head_checks:
                    if not header_cells:
                        break
                    check_func = getattr(check['func'], 'check_headers', check['func'])
                    errors += check_func(header_cells, sample) or []
                # That's a hack to make head/body checks happen
                for check in checks:
                    if not header_cells:
                        break
                    check_func = getattr(check['func'], 'check_headers_hook', None)
                    if check_func:
                        errors += check_func(header_cells, sample) or []
                for error in errors:
                    error.row = None

            # Grab fields from cells, as there might have been new ones
            # inferred by the "extra-header" check
            fields = [c.get('field') for c in header_cells]

        # Body checks
        if not fatal_error:
            body_checks = _filter_checks(checks, context='body')
            with stream:
                extended_rows = stream.iter(extended=True)
                while True:
                    try:
                        row_number, _, row = next(extended_rows)
                    except StopIteration:
                        break
                    except Exception as exception:
                        error, fatal_error = _compose_error_from_exception(exception)
                        errors.append(error)
                        break
                    row_cells = cells.create_cells(headers, fields, row, row_number)
                    for check in body_checks:
                        if not row_cells:
                            break
                        check_func = getattr(check['func'], 'check_row', check['func'])
                        errors += check_func(row_cells) or []
                    for error in reversed(errors):
                        if error.row is not None:
                            break
                        error.row = row
                    if row_number >= self.__row_limit:
                        warnings.append(
                            'Table "%s" inspection has reached %s row(s) limit'
                            % (source, self.__row_limit)
                        )
                        break
                    if len(errors) >= self.__error_limit:
                        warnings.append(
                            'Table "%s" inspection has reached %s error(s) limit'
                            % (source, self.__error_limit)
                        )
                        break

        # Table checks
        if not fatal_error:
            for check in checks:
                check_func = getattr(check['func'], 'check_table', None)
                if check_func:
                    errors += check_func() or []

        # Stop timer
        stop = datetime.datetime.now()

        # Compose report
        headers = headers if any(elt is not None for elt in headers) else None
        if self.__error_limit != float('inf'):
            errors = errors[: self.__error_limit]
        errors = sorted(errors)
        report = copy(extra)
        report.update(
            {
                'time': round((stop - start).total_seconds(), 3),
                'valid': not bool(errors),
                'error-count': len(errors),
                'row-count': row_number,
                'source': source,
                'headers': headers,
                'scheme': stream.scheme,
                'format': stream.format,
                'encoding': stream.encoding,
                'schema': 'table-schema' if schema else None,
                'errors': [dict(error) for error in errors],
            }
        )

        return warnings, _clean_empty(report)


# Internal


def _filter_checks(checks, type=None, context=None, inverse=False):
    result = []
    comparator = operator.eq if inverse else operator.ne
    for check in checks:
        if type and comparator(check['type'], type):
            continue
        if context and comparator(check['context'], context):
            continue
        result.append(check)
    return result


def _compose_error_from_exception(exception):
    code = 'source-error'
    message = str(exception)
    fatal_error = True

    if isinstance(exception, tabulator.exceptions.SourceError):
        code = 'source-error'
    elif isinstance(exception, tabulator.exceptions.SchemeError):
        code = 'scheme-error'
    elif isinstance(exception, tabulator.exceptions.FormatError):
        code = 'format-error'
    elif isinstance(exception, tabulator.exceptions.EncodingError):
        code = 'encoding-error'
    elif isinstance(exception, tabulator.exceptions.IOError):
        code = 'io-error'
    elif isinstance(exception, tabulator.exceptions.HTTPError):
        code = 'http-error'
    elif isinstance(exception, tableschema.exceptions.IntegrityError):
        code = 'source-error'
        fatal_error = False

    return (Error(code, message=message), fatal_error)


def _compose_error_from_schema_error(error):
    message_substitutions = {
        'error_message': error,
    }
    return Error('schema-error', message_substitutions=message_substitutions)


def _clean_empty(d):
    """Remove None values from a dict."""
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (_clean_empty(v) for v in d) if v is not None]
    return {
        k: v for k, v in ((k, _clean_empty(v)) for k, v in d.items()) if v is not None
    }
