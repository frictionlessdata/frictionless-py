# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import os
import json
import datetime
from six.moves import zip_longest
from multiprocessing.pool import ThreadPool
from . import checks as checks_module
from . import exceptions
from . import profiles


# Module API

class Inspector(object):
    """Datasets inspector.

    Args:
        checks (str/dict): inspection checks
        table_limit (int): upper limit for tables
        row_limit (int): upper limit for rows
        error_limit (int): upper limit for errors

    """

    # Public

    def __init__(self,
                 checks='all',
                 table_limit=None,
                 row_limit=None,
                 error_limit=None):

        # Defaults
        if table_limit is None:
            table_limit = 10
        if row_limit is None:
            row_limit = 1000
        if error_limit is None:
            error_limit = 1000

        # Set attributes
        self.__checks = self.__prepare_checks(checks)
        self.__table_limit = table_limit
        self.__row_limit = row_limit
        self.__error_limit = error_limit

    def inspect(self, source, profile=None, **options):
        """Inspect source with given profile and options.

        Args:
            source (mixed): source to inspect
            profile (str): dataset profile
                supported profiles:
                    - table (default)
                    - datapackage
                    - ckan
            options (dict): source options

        Returns:
            dict: report

        """

        # Start timer
        start = datetime.datetime.now()

        # Defaults
        if profile is None:
            profile = 'table'

        # Prepare vars
        tables = []
        extras = []
        errors = []
        reports = []
        fatal_error = False

        # Get profile function
        if not hasattr(profiles, profile):
            message = 'Profile "%s" is not supported' % profile
            raise exceptions.GoodtablesException(message)
        profile_func = getattr(profiles, profile)

        # Get tables/extras
        try:
            dataset = profile_func(source, **options)
            for count, item in enumerate(dataset, start=1):
                tables.append(item['table'])
                extras.append(item['extra'])
                if count >= self.__table_limit:
                    break
        except Exception as exception:
            fatal_error = True
            checks = self.__filter_checks(context='dataset')
            for check in checks:
                for error in check['func'](exception):
                    error.update({
                        'row': None,
                        'code': check['code'],
                    })
                    errors.append(error)
            if not errors:
                raise

        # Collect reports
        if not fatal_error:
            tasks = []
            pool = ThreadPool(processes=len(tables))
            for table in tables:
                tasks.append(pool.apply_async(
                    self.__inspect_table, (table,)))
            for task, extra in zip(tasks, extras):
                report = task.get()
                report.update(extra)
                reports.append(report)

        # Stop timer
        stop = datetime.datetime.now()

        # Compose report
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

        # Table checks
        try:
            table.stream.open()
            stream = table.stream
            schema = None
            if self.__filter_checks(type='schema'):
                # Schema infer if needed
                schema = table.schema
            headers = stream.headers
            sample = stream.sample
        except Exception as exception:
            fatal_error = True
            checks = self.__filter_checks(context='table')
            for check in checks:
                for error in check['func'](exception):
                    error.update({
                        'row': None,
                        'code': check['code'],
                    })
                    errors.append(error)
            if not errors:
                raise

        # Prepare columns
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
            checks = self.__filter_checks(context='head')
            for check in checks:
                for error in check['func'](columns, sample):
                    if not columns:
                        break
                    error.update({
                        'row': None,
                        'code': check['code'],
                    })
                    errors.append(error)

        # Body checks
        if not fatal_error:
            states = {}
            checks = self.__filter_checks(context='body')
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
                        for error in check['func'](row_number, columns, state):
                            error.update({
                                'row': row,
                                'code': check['code'],
                            })
                            errors.append(error)
                    if len(errors) >= self.__error_limit:
                        break

        # Stop timer
        stop = datetime.datetime.now()

        # Compose report
        errors = errors[:self.__error_limit]
        report = {
            'time': round((stop - start).total_seconds(), 3),
            'valid': not bool(errors),
            'error-count': len(errors),
            'row-count': row_number,
            'headers': headers,
            'errors': errors,
        }

        return report

    def __prepare_checks(self, config):

        # Load spec
        base = os.path.dirname(__file__)
        path = os.path.join(base, 'spec.json')
        spec = json.load(io.open(path, encoding='utf-8'))

        # Get all checks
        checks = []
        for check in spec['checks']:
            attr = check['code'].replace('-', '_')
            if not hasattr(checks_module, attr):
                message = 'Check "%s" is not supported' % check['code']
                raise exceptions.GoodtablesException(message)
            func = getattr(checks_module, attr)
            check['func'] = func
            checks.append(check)

        # All checks
        if config == 'all':
            pass

        # Structure checks
        elif config == 'structure':
            checks = [check for check in checks
                if check['type'] in ['source', 'structure']]

        # Schema checks
        elif config == 'schema':
            checks = [check for check in checks
                if check['type'] in ['source', 'schema']]

        # Custom checks
        elif isinstance(config, dict):
            default = True not in config.values()
            checks = [check for check in checks
                if check['type'] in ['source'] or
                config.get(check['code'], default)]

        # Unknown checks
        else:
            message = 'Checks config "%s" is not supported' % config
            raise exceptions.GoodtablesException(message)

        # Ensure requires
        codes = set()
        for check in checks:
            if not set(check['requires']).issubset(codes):
                message = 'Check "%s" requires all checks "%s" before'
                message = message % (check['code'], check['requires'])
                raise exceptions.GoodtablesException(message)
            codes.add(check['code'])

        return checks

    def __filter_checks(self, type=None, context=None):

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
