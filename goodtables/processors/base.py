# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import tellme
from ..utilities import helpers
from .. import datatable
from .. import exceptions

class Processor(object):
    
    """Base Processor class. Processor implementations should inherit."""
    
    name = None
    ROW_LIMIT_MAX = 30000
    REPORT_LIMIT_MAX = 1000
    RESULT_CATEGORY_HEADER = 'header'
    RESULT_CATEGORY_ROW = 'row'
    RESULT_CATEGORY_COLUMN = 'column'
    RESULT_CATEGORY_FILE = 'file'
    RESULT_LEVEL_ERROR = 'error'
    RESULT_LEVEL_WARNING = 'warning'
    RESULT_LEVEL_INFO = 'info'
    RESULT_HEADER_ROW_NAME = 'headers'
    RAISES = (exceptions.ProcessorBuildError,)

    def __init__(self, fail_fast=False, transform=True, row_limit=30000,
                 header_index=0, report=None, report_limit=1000,
                 report_stream=None, result_level='error'):

        self.name = self.name or self.__class__.__name__.lower()
        self.fail_fast = fail_fast
        self.transform = True
        self.row_limit = self.get_row_limit(row_limit)
        self.report_limit = self.get_report_limit(report_limit)
        self.header_index = header_index
        self.row_count = None
        self.result_level = result_level

        if report is None:
            if report_stream:
                report_stream_tests = [isinstance(report_stream, io.TextIOBase),
                                       report_stream.writable(),
                                       report_stream.seekable()]

                if not all(report_stream_tests):
                    _msg = '`report_stream` must be a seekable and writable text stream.'
                    raise exceptions.ProcessorBuildError(_msg)

                report_backend = 'client'
            else:
                report_backend = 'yaml'

            report_options = {
                'schema': helpers.report_schema,
                'backend': report_backend,
                'client_stream': report_stream,
                'limit': report_limit
            }

            self.report = tellme.Report(self.name, **report_options)
        else:
            self.report = report

    def get_row_limit(self, passed_limit):
        """Return the row limit, locked to an upper limit."""

        if passed_limit > self.ROW_LIMIT_MAX:
            return self.ROW_LIMIT_MAX
        else:
            return passed_limit

    def get_report_limit(self, passed_limit):
        """Return the report_limit, locked to an upper limit."""

        if passed_limit > self.REPORT_LIMIT_MAX:
            return self.REPORT_LIMIT_MAX
        else:
            return passed_limit

    def get_row_id(self, headers, row):
        """Return an identifying for a row, or None if not able to detect."""
        ids = ('id', '_id')
        for k, v in zip(headers, row):
            if k in ids:
                return v
        return ''

    def make_entry(self, processor, result_category, result_level,
                   result_message, result_id, result_name, result_context,
                   row_index=None, row_name='', column_index=None, column_name=''):
        """Return a report entry."""
    
        return {
            'processor': processor,
            'result_category': result_category,
            'result_level': result_level,
            'result_message': result_message,
            'result_id': result_id,
            'result_name': result_name,
            'result_context': result_context,
            'row_index': row_index,
            'row_name': row_name,
            'column_index': column_index,
            'column_name': column_name
        }

    def run(self, data_source, headers=None, format='csv', encoding=None,
            decode_strategy='replace', is_table=False):
        """Run this processor on data_source.

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
            try:
                data = datatable.DataTable(data_source, headers=headers,
                                           format=format, encoding=encoding,
                                           decode_strategy=decode_strategy,
                                           header_index=self.header_index)
                openfiles.extend(data.openfiles)
            except datatable.DataTable.RAISES as e:
                valid = False
                data = None
                if isinstance(e, exceptions.DataSourceHTTPError):
                    error_type = 'http_{0}_error'.format(e.status)
                elif isinstance(e, exceptions.DataSourceDecodeError):
                    error_type = 'data_decode_error'
                elif isinstance(e, exceptions.DataSourceFormatUnsupportedError):
                    error_type = 'data_{0}_error'.format(e.file_format)
                elif isinstance(e, exceptions.DataSourceMalformatedError):
                    error_type = 'invalid_{0}_error'.format(format)
                    
                entry = self.make_entry(
                    processor='base',
                    result_category=self.RESULT_CATEGORY_FILE,
                    result_level=self.RESULT_LEVEL_ERROR,
                    result_message=e.msg,
                    result_id=error_type,
                    result_name=e.name,
                    result_context=[]
                )
                    
                self.report.write(entry)
                return valid, self.report, ''

        # pre_run
        if hasattr(self, 'pre_run'):
            _valid, data = self.pre_run(data)
            valid = _run_valid(_valid, valid)
            if not _valid and self.fail_fast:
                return valid, self.report, data

        # run_header
        if hasattr(self, 'run_header'):
            _valid, data.headers = self.run_header(data.headers,
                                                   header_index=self.header_index)
            valid = _run_valid(_valid, valid)
            if not _valid and self.fail_fast:
                return valid, self.report, data

        # run_row
        if hasattr(self, 'run_row'):
            # TODO: on transform, create a new stream out of returned rows
            for index, row in enumerate(data.values):
                if index < self.row_limit:
                    # keep a count of rows processed
                    self.row_count = (index + 1)
                    _valid, data.headers, index, row = self.run_row(data.headers, index, row)
                    valid = _run_valid(_valid, valid)
                    if not _valid and self.fail_fast:
                        return valid, self.report, data

        # post_run
        if hasattr(self, 'post_run'):
            _valid, data = self.post_run(data)
            valid = _run_valid(_valid, valid)
            if not _valid and self.fail_fast:
                return valid, self.report, data

        for f in openfiles:
            f.close()

        return valid, self.report, data
