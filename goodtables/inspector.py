# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import operator
import tabulator
from copy import copy
from six.moves import zip_longest
from jsontableschema import Schema, infer
from multiprocessing.pool import ThreadPool
from .registry import registry
from . import exceptions
from . import config


# Module API

class Inspector(object):

    # Public

    def __init__(self,
                 checks='spec',
                 infer_schema=False,
                 infer_fields=False,
                 order_fields=False,
                 error_limit=config.DEFAULT_ERROR_LIMIT,
                 table_limit=config.DEFAULT_TABLE_LIMIT,
                 row_limit=config.DEFAULT_ROW_LIMIT):
        """https://github.com/frictionlessdata/goodtables-py#inspector
        """

        # Set attributes
        self.__checks = checks
        self.__infer_schema = infer_schema
        self.__infer_fields = infer_fields
        self.__order_fields = order_fields
        self.__error_limit = error_limit
        self.__table_limit = table_limit
        self.__row_limit = row_limit

    def inspect(self, source, preset='table', **options):
        """https://github.com/frictionlessdata/goodtables-py#inspector
        """

        # Start timer
        start = datetime.datetime.now()

        # Prepare preset
        try:
            presets = registry.compile_presets()
            preset_func = presets[preset]['func']
            if preset == 'nested':
                options['presets'] = presets
        except KeyError:
            message = 'Preset "%s" is not registered' % preset
            raise exceptions.GoodtablesException(message)

        # Prepare tables
        warnings, tables = preset_func(source, **options)
        if len(tables) > self.__table_limit:
            warnings.append(
                'Dataset inspection has reached %s table(s) limit' %
                (self.__table_limit))
            tables = tables[:self.__table_limit]

        # Collect table reports
        table_reports = []
        if tables:
            tasks = []
            pool = ThreadPool(processes=len(tables))
            for table in tables:
                tasks.append(pool.apply_async(self.__inspect_table, (table,)))
            for task in tasks:
                table_warnings, table_report = task.get()
                warnings.extend(table_warnings)
                table_reports.append(table_report)

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
        }

        return report

    # Internal

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
        checks = registry.compile_checks(self.__checks,
            order_fields=self.__order_fields, infer_fields=self.__infer_fields)

        # Prepare table
        try:
            stream.open()
            sample = stream.sample
            headers = stream.headers
            if headers is None:
                headers = [None] * len(sample[0]) if sample else []
            if _filter_checks(checks, type='schema'):
                if schema is None and self.__infer_schema:
                    schema = Schema(infer(headers, sample))
            if schema is None:
                checks = _filter_checks(checks, type='schema', inverse=True)
        except Exception as exception:
            fatal_error = True
            error = _compose_error_from_exception(exception)
            errors.append(error)

        # Prepare columns
        if not fatal_error:
            columns = []
            fields = [None] * len(headers)
            if schema is not None:
                fields = schema.fields
            iterator = zip_longest(headers, fields, fillvalue=_FILLVALUE)
            for number, (header, field) in enumerate(iterator, start=1):
                column = {'number': number}
                if header is not _FILLVALUE:
                    column['header'] = header
                if field is not _FILLVALUE:
                    column['field'] = field
                columns.append(column)

        # Head checks
        if not fatal_error:
            if None not in headers:
                head_checks = _filter_checks(checks, context='head')
                for check in head_checks:
                    if not columns:
                        break
                    check_func = getattr(check['func'], 'check_headers', check['func'])
                    check_func(errors, columns, sample)
                for error in errors:
                    error['row'] = None

        # Body checks
        if not fatal_error:
            colmap = {column['number']: column for column in columns}
            body_checks = _filter_checks(checks, context='body')
            with stream:
                extended_rows = stream.iter(extended=True)
                while True:
                    try:
                        row_number, _, row = next(extended_rows)
                    except StopIteration:
                        break
                    except Exception as exception:
                        fatal_error = True
                        error = _compose_error_from_exception(exception)
                        errors.append(error)
                        break
                    columns = []
                    iterator = zip_longest(headers, row, fillvalue=_FILLVALUE)
                    for number, (header, value) in enumerate(iterator, start=1):
                        colref = colmap.get(number, {})
                        column = {'number': number}
                        if header is not _FILLVALUE:
                            column['header'] = colref.get('header', header)
                        if 'field' in colref:
                            column['field'] = colref['field']
                        if value is not _FILLVALUE:
                            column['value'] = value
                        columns.append(column)
                    for check in body_checks:
                        if not columns:
                            break
                        check_func = getattr(check['func'], 'check_row', check['func'])
                        check_func(errors, columns, row_number)
                    for error in reversed(errors):
                        if 'row' in error:
                            break
                        error['row'] = row
                    if row_number >= self.__row_limit:
                        warnings.append(
                            'Table "%s" inspection has reached %s row(s) limit' %
                            (source, self.__row_limit))
                        break
                    if len(errors) >= self.__error_limit:
                        warnings.append(
                            'Table "%s" inspection has reached %s error(s) limit' %
                            (source, self.__error_limit))
                        break

        # Table checks
        for check in checks:
            check_func = getattr(check['func'], 'check_table', None)
            if check_func:
                check_func(errors)

        # Stop timer
        stop = datetime.datetime.now()

        # Compose report
        headers = headers if None not in headers else None
        errors = errors[:self.__error_limit]
        errors = _sort_errors(errors)
        report = copy(extra)
        report.update({
            'time': round((stop - start).total_seconds(), 3),
            'valid': not bool(errors),
            'error-count': len(errors),
            'row-count': row_number,
            'source': source,
            'headers': headers,
            'scheme': stream.scheme,
            'format': stream.format,
            'encoding': stream.encoding,
            'errors': errors,
        })

        return warnings, report


# Internal

_FILLVALUE = '_FILLVALUE'


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
    return {
        'row': None,
        'code': code,
        'message': message,
        'row-number': None,
        'column-number': None,
    }


def _sort_errors(errors):
    return sorted(errors, key=lambda error:
        (error['row-number'] or 0, error['column-number']))
