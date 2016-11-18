# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

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
        self.__infer_fields = infer_fields
        self.__order_fields = order_fields
        self.__presets = self.__prepare_presets(copy(custom_presets))
        self.__checks = self.__prepare_checks(checks, copy(custom_checks))

    def inspect(self, source, preset='table', **options):
        """Inspect source with given preset and options.

        Args:
            source (mixed): source to inspect
            preset (str): dataset extraction preset
                supported presets:
                    - table
                    - datapackage
            options (dict): source options

        Returns:
            dict: report

        """

        # Start timer
        start = datetime.datetime.now()

        # Prepare preset
        try:
            preset_func = self.__presets[preset]
        except KeyError:
            message = 'Preset "%s" is not registered' % preset
            raise exceptions.GoodtablesException(message)

        # Prepare tables
        errors, tables = preset_func(source, **options)
        tables = tables[:self.__table_limit]
        for error in errors:
            error['row'] = None

        # Collect reports
        reports = []
        if not errors:
            tasks = []
            pool = ThreadPool(processes=len(tables))
            for table in tables:
                tasks.append(pool.apply_async(self.__inspect_table, (table,)))
            for task in tasks:
                report = task.get()
                reports.append(report)

        # Stop timer
        stop = datetime.datetime.now()

        # Compose report
        errors = errors[:self.__error_limit]
        report = {
            'time': round((stop - start).total_seconds(), 3),
            'valid': not bool(errors) and all(report['valid'] for report in reports),
            'error-count': len(errors) + sum(len(report['errors']) for report in reports),
            'table-count': len(tables),
            'tables': reports,
            'errors': errors,
        }

        return report

    # Internal

    def __inspect_table(self, table):

        # Start timer
        start = datetime.datetime.now()

        # Prepare vars
        errors = []
        headers = None
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
            if self.__filter_checks(checks, type='schema'):
                if schema is None and self.__infer_schema:
                    schema = Schema(infer(headers, sample))
            if schema is None:
                checks = self.__filter_checks(checks, type='schema', inverse=True)
        except Exception as exception:
            fatal_error = True
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
            else:
                raise
            errors.append({
                'row': None,
                'code': code,
                'message': message,
                'row-number': None,
                'column-number': None,
            })

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
            head_checks = self.__filter_checks(checks, context='head')
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
            body_checks = self.__filter_checks(checks, context='body')
            with stream:
                for row_number, headers, row in stream.iter(extended=True):
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
                        break
                    if len(errors) >= self.__error_limit:
                        break

        # Stop timer
        stop = datetime.datetime.now()

        # Compose report
        errors = errors[:self.__error_limit]
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

        return report

    def __prepare_presets(self, custom):

        # Prepare presets
        presets = {}
        for preset in chain(vars(presets_module).values(), custom):
            descriptor = getattr(preset, 'preset', None)
            if descriptor:
                presets[descriptor['name']] = preset

        return presets

    def __prepare_checks(self, setup, custom):

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
            checks = self.__filter_checks(checks, type='structure')

        # Filter schema checks
        elif setup == 'schema':
            checks = self.__filter_checks(checks, type='schema')

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
            args, _, _, _ = inspect.getargspec(check['func'])
            if 'order_fields' in args:
                check['func'] = partial(check['func'],
                    order_fields=self.__order_fields)
            if 'infer_fields' in args:
                check['func'] = partial(check['func'],
                    infer_fields=self.__infer_fields)

        return checks

    def __filter_checks(self, checks, type=None, context=None, inverse=False):

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


# Internal

_FILLVALUE = '_FILLVALUE'
