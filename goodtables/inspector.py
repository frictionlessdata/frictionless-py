# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import os
import json
import inspect
import datetime
import tabulator
from copy import copy
from itertools import chain
from functools import partial
from six.moves import zip_longest
from multiprocessing.pool import ThreadPool
from . import profiles as profiles_module
from . import checks as checks_module
from . import exceptions


# Module API

class Inspector(object):
    """Datasets inspector.

    Args:
        checks (str/dict): checks filter
        table_limit (int): upper limit for tables
        row_limit (int): upper limit for rows
        error_limit (int): upper limit for errors
        order_fields (bool): allow field ordering
        infer_fields (bool): allow field inferring

    """

    # Public

    def __init__(self,
                 checks='all',
                 table_limit=10,
                 row_limit=1000,
                 error_limit=1000,
                 order_fields=False,
                 infer_fields=False,
                 custom_profiles=[],
                 custom_checks=[]):

        # Set attributes
        self.__table_limit = table_limit
        self.__row_limit = row_limit
        self.__error_limit = error_limit
        self.__order_fields = copy(order_fields)
        self.__infer_fields = copy(infer_fields)
        self.__profiles = self.__prepare_profiles(custom_profiles)
        self.__checks = self.__prepare_checks(checks, custom_checks)

    def inspect(self, source, profile='table', **options):
        """Inspect source with given profile and options.

        Args:
            source (mixed): source to inspect
            profile (str): dataset profile
                supported profiles:
                    - table
                    - datapackage
                    - ckan
            options (dict): source options

        Returns:
            dict: report

        """

        # Start timer
        start = datetime.datetime.now()

        # Prepare vars
        errors = []
        tables = []
        reports = []

        # Prepare profile
        try:
            profile_func = self.__profiles[profile]
        except KeyError:
            message = 'Profile "%s" is not registered' % profile
            raise exceptions.GoodtablesException(message)

        # Prepare tables
        profile_func(errors, tables, source, **options)
        tables = tables[:self.__table_limit]
        for error in errors:
            error['row'] = None

        # Collect reports
        if not errors:
            tasks = []
            pool = ThreadPool(processes=len(tables))
            for table in tables:
                tasks.append(pool.apply_async(
                    self.__inspect_table, (table['table'], table['extra'])))
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

    def __inspect_table(self, table, extra):

        # Start timer
        start = datetime.datetime.now()

        # Prepare vars
        errors = []
        headers = None
        row_number = 0
        fatal_error = False

        # Prepare table
        try:
            table.stream.open()
            stream = table.stream
            schema = None
            if self.__get_checks(type='schema'):
                # Schema infer if needed
                schema = table.schema
            headers = stream.headers
            sample = stream.sample
        except Exception as exception:
            fatal_error = True
            # https://github.com/frictionlessdata/goodtables-py/issues/115
            if isinstance(exception, tabulator.exceptions.TabulatorException):
                code = 'io-error'
                message = 'IO error'
            elif isinstance(exception, tabulator.exceptions.TabulatorException):
                code = 'http-error'
                message = 'HTTP error'
            elif isinstance(exception, tabulator.exceptions.TabulatorException):
                code = 'scheme-error'
                message = 'Scheme error'
            elif isinstance(exception, tabulator.exceptions.TabulatorException):
                code = 'format-error'
                message = 'Format error'
            elif isinstance(exception, tabulator.exceptions.TabulatorException):
                code = 'encoding-error'
                message = 'Encoding error'
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
            checks = self.__get_checks(context='head')
            for check in checks:
                if not columns:
                    break
                check['func'](errors, columns, sample)
            for error in errors:
                error['row'] = None

        # Body checks
        if not fatal_error:
            states = {}
            checks = self.__get_checks(context='body')
            colmap = {column['number']: column for column in columns}
            with stream:
                for row_number, headers, row in stream.iter(extended=True):
                    if row_number >= self.__row_limit:
                        break
                    columns = []
                    iterator = zip_longest(headers, row, fillvalue=_FILLVALUE)
                    for number, (header, value) in enumerate(iterator, start=1):
                        column = {'number': number}
                        if header is not _FILLVALUE:
                            colref = colmap.get(number, {})
                            column['header'] = colref.get('header') or header
                            column['field'] = colref.get('field')
                        if value is not _FILLVALUE:
                            column['value'] = value
                        columns.append(column)
                    for check in checks:
                        if not columns:
                            break
                        state = states.setdefault(check['code'], {})
                        check['func'](errors, columns, row_number, state)
                    for error in reversed(errors):
                        if 'row' in error:
                            break
                        error['row'] = row
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
            'errors': errors,
        })

        return report

    def __prepare_profiles(self, custom):

        # Prepare profiles
        profiles = {}
        for profile in chain(vars(profiles_module).values(), custom):
            descriptor = getattr(profile, 'profile', None)
            if descriptor:
                profiles[descriptor['name']] = profile

        return profiles

    def __prepare_checks(self, config, custom):

        # Prepare errors/checkmap
        errors = []
        checkmap = {}
        base = os.path.dirname(__file__)
        path = os.path.join(base, 'spec.json')
        spec = json.load(io.open(path, encoding='utf-8'))
        errors.extend(spec['errors'])
        for check in chain(vars(checks_module).values(), custom):
            descriptor = getattr(check, 'check', None)
            if descriptor:
                error = descriptor['error']
                errormap = {error['code']: index for index, error in enumerate(errors)}
                if descriptor['before'] in errormap:
                    errors.insert(errormap[descriptor['before']], error)
                if descriptor['after'] in errormap:
                    errors.insert(errormap[descriptor['after']] + 1, error)
                checkmap[error['code']] = check

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
        if config == 'structure':
            checks = [check for check in checks
                if check['type'] == 'structure']

        # Filter schema checks
        elif config == 'schema':
            checks = [check for check in checks
                if check['type'] == 'schema']

        # Filter granular checks
        elif isinstance(config, dict):
            default = True not in config.values()
            checks = [check for check in checks
                if config.get(check['code'], default)]

        # Unknown filter
        elif config != 'all':
            message = 'Checks filter "%s" is not supported' % config
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

    def __get_checks(self, type=None, context=None):

        # Filted checks
        checks = []
        for check in self.__checks:
            if type and check['type'] != type:
                continue
            if context and check['context'] != context:
                continue
            checks.append(check)

        return checks


# Internal

_FILLVALUE = '_FILLVALUE'
