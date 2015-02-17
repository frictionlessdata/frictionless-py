# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import tellme
from ..utilities import data_table, helpers


class Validator(object):

    """Base Validator class. Validator implementations should inherit."""

    name = None

    def __init__(self, fail_fast=False, transform=False, report_limit=1000,
                 row_limit=30000, report_stream=None):

        self.name = self.name or self.__class__.__name__.lower()
        self.fail_fast = fail_fast
        self.transform = transform
        if row_limit <= 30000:
            self.row_limit = row_limit
        else:
            self.row_limit = 30000
        if report_limit <= 1000:
            self.report_limit = report_limit
        else:
            self.report_limit = 1000

        if report_stream:
            report_backend = 'client'
        else:
            report_backend = 'yaml'

        report_options = {
            'schema': helpers.report_schema,
            'backend': report_backend,
            'client_stream': report_stream
        }
        self.report = tellme.Report(self.name, **report_options)

    def run(self, data_source, headers=None, is_table=False):

        """Run this validator on data_source.

        Args:
            data_source: the data source as string, URL, filepath or stream
            headers: pass headers explicitly to the DataTable constructor
            is_table: if True, data_source is a DataTable instance

        Returns:
            a tuple of `valid, report, data_table`
            valid: boolean indicating if the data is valid
            report: instance of reporter.Report
            data: a data_table.DataTable object containing the output data

        """

        def _run_valid(process_valid, run_valid):
            """Set/maintain the valid state of the run."""
            if not process_valid and run_valid:
                return False
            return run_valid

        valid = True
        openfiles = []

        if is_table:
            data = data_source
        else:
            data = data_table.DataTable(data_source, headers=headers)
            openfiles.extend(data.openfiles)

        # pre_run
        if hasattr(self, 'pre_run'):
            _valid, data = self.pre_run(data)
            valid = _run_valid(_valid, valid)
            if not _valid and self.fail_fast:
                return valid, self.report

        # run_header
        if hasattr(self, 'run_header'):
            _valid, data.headers = self.run_header(data.headers)
            valid = _run_valid(_valid, valid)
            if not _valid and self.fail_fast:
                return valid, self.report

        # run_row
        if hasattr(self, 'run_row'):
            # TODO: on transform, create a new stream out of returned rows
            for index, row in enumerate(data.values):
                if index < self.row_limit:
                    _valid, data.headers, index, row = self.run_row(data.headers, index, row)
                    valid = _run_valid(_valid, valid)
                    if not _valid and self.fail_fast:
                        return valid, self.report

        # post_run
        if hasattr(self, 'post_run'):
            _valid, data = self.post_run(data)
            valid = _run_valid(_valid, valid)
            if not _valid and self.fail_fast:
                return valid, self.report

        for f in openfiles:
            f.close()

        return valid, self.report, data
