# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import six
import inspect
import datetime
import operator
import tabulator
from copy import copy
from itertools import chain
from functools import partial
from six.moves import zip_longest
from jsontableschema import Schema, infer
from multiprocessing.pool import ThreadPool
from . import presets as presets_module
from . import checks as checks_module
from . import exceptions
from . import config
from .spec import spec


# Module API

class Inspector(object):
    """Datasets inspector.

    Args:
        checks (str/dict): checks filter
        error_limit (int): upper limit for errors
        table_limit (int): upper limit for tables
        row_limit (int): upper limit for rows
        order_fields (bool): allow field ordering
        infer_fields (bool): allow field inferring

    """

    # Public

    def __init__(self,
                 checks='all',
                 error_limit=1000,
                 table_limit=10,
                 row_limit=1000,
                 infer_schema=False,
                 infer_fields=False,
                 order_fields=False,
                 custom_presets=[],
                 custom_checks=[]):

        # Set attributes
        self.__error_limit = error_limit
        self.__table_limit = table_limit
        self.__row_limit = row_limit
        self.__infer_schema = infer_schema
        self.__presets = _prepare_presets(copy(custom_presets))
        self.__checks = _prepare_checks(checks, copy(custom_checks),
            order_fields=order_fields, infer_fields=infer_fields)

    def inspect(self, source, preset='table', **options):
        """Inspect source with given preset and options.

        Args:
            source (mixed): source to inspect
            preset (str): dataset extraction preset
                supported presets:
                    - table
                    - tables
                    - datapackage
                    - datapackages
            options (dict): source options

        Returns:
            dict: report

        """

        # Start timer
        start = datetime.datetime.now()

        # Prepare preset
        try:
            preset_func = self.__presets[preset]
            if preset == 'nested':
                options['presets'] = self.__presets
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
        checks = copy(self.__checks)
        source = table['source']
        stream = table['stream']
        schema = table['schema']
        extra = table['extra']

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
                    check['func'](errors, columns, sample)
                for error in errors:
                    error['row'] = None

        # Body checks
        if not fatal_error:
            states = {}
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
                        state = states.setdefault(check['code'], {})
                        check['func'](errors, columns, row_number, state)
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
            'headers': headers,
            'source': source,
            'errors': errors,
        })

        return warnings, report


# Internal

_FILLVALUE = '_FILLVALUE'


def _prepare_presets(custom):

    # Prepare presets
    presets = {}
    for preset in chain(vars(presets_module).values(), custom):
        descriptor = getattr(preset, 'preset', None)
        if descriptor:
            presets[descriptor['name']] = preset

    return presets


def _prepare_checks(setup, custom, order_fields, infer_fields):

    # Prepare errors/checkmap
    errors = []
    checkmap = {}
    for code in config.CHECKS:
        error = copy(spec['errors'][code])
        error.update({'code': code})
        errors.append(error)
    for check in chain(vars(checks_module).values(), custom):
        desc = getattr(check, 'check', None)
        if desc:
            errormap = {error['code']: index for index, error in enumerate(errors)}
            if desc['before'] in errormap:
                errors.insert(errormap[desc['before']], desc)
            if desc['after'] in errormap:
                errors.insert(errormap[desc['after']] + 1, desc)
            checkmap[desc['code']] = check

    # Prepare checks
    checks = []
    for error in errors:
        if error['code'] in checkmap:
            checks.append({
                'func': checkmap[error['code']],
                'code': error['code'],
                'type': error['type'],
                'context': error['context'],
            })

    # Filter structure checks
    if setup == 'structure':
        checks = _filter_checks(checks, type='structure')

    # Filter schema checks
    elif setup == 'schema':
        checks = _filter_checks(checks, type='schema')

    # Filter granular checks
    elif isinstance(setup, dict):
        default = True not in setup.values()
        checks = [check for check in checks
            if setup.get(check['code'], default)]

    # Unknown filter
    elif setup != 'all':
        message = 'Checks filter "%s" is not supported' % setup
        raise exceptions.GoodtablesException(message)

    # Bind options
    for check in checks:
        if six.PY2:
            parameters, _, _, _ = inspect.getargspec(check['func'])
        else:
            parameters = inspect.signature(check['func']).parameters
        if 'order_fields' in parameters:
            check['func'] = partial(check['func'], order_fields=order_fields)
        if 'infer_fields' in parameters:
            check['func'] = partial(check['func'], infer_fields=infer_fields)

    return checks


def _filter_checks(checks, type=None, context=None, inverse=False):

    # Filted checks
    result = []
    comparator = operator.ne
    if inverse:
        comparator = operator.eq
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
