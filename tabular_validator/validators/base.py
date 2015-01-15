import reporter
from .. import utilities


class Validator(object):

    """Base Validator class. Validator implementations should inherit."""

    def __init__(self, name=None, fail_fast=False, transform=True, report_limit=1000):
        self.name = name or self.__class__.__name__.lower()
        self.fail_fast = fail_fast
        self.transform = transform
        self.report_limit = report_limit
        self.report = reporter.Report(self.name)

    def run(self, data_source, headers=None, is_table=False):

        """Run this validator on data_source.

        Args:
            data_source: the data source as string, URL, filepath or stream
            headers: pass headers explicitly to the DataTable constructor
            is_table: if True, data_source is a DataTable instance

        Returns:
            a tuple of `valid, report`
            valid: boolean indicating if the data is valid
            report: instance of reporter.Report

        """

        # The valid state of the run
        valid = True

        # if is_table, then data_source is already a table
        if is_table:
            table = data_source
        else:
            table = utilities.DataTable(data_source, headers=headers)

        def _run_valid(process_valid, run_valid):
            """Set/maintain the valid state of the run."""
            if not process_valid and run_valid:
                return False
            return True

        # pre_run
        if hasattr(self, 'pre_run'):
            _valid, table = self.pre_run(table)
            valid = _run_valid(_valid, valid)
            if not _valid and self.fail_fast:
                return valid, self.report

        # run_header
        if hasattr(self, 'run_header'):
            _valid, table.headers = self.run_header(table.headers)
            valid = _run_valid(_valid, valid)
            if not _valid and self.fail_fast:
                return valid, self.report

        # run_row
        if hasattr(self, 'run_row'):
            # TODO: on transform, create a new stream out of returned rows
            for index, row in enumerate(table.values):
                _valid, row = self.run_row(table.headers, index, row)
                valid = _run_valid(_valid, valid)
                if not _valid and self.fail_fast:
                    return valid, self.report

        # run_column
        # TODO: ensure work is on transformed data (after run_row)
        # if hasattr(self, 'run_column'):
        #     for index, column in enumerate(table.by_column):
        #         _valid, column = self.run_column(index, column)
        #         valid = _run_valid(_valid, valid)
        #         if not _valid and self.fail_fast:
        #             return valid, self.report

        # post_run
        if hasattr(self, 'post_run'):
            _valid, table = self.post_run(table)
            valid = _run_valid(_valid, valid)
            if not _valid and self.fail_fast:
                return valid, self.report

        return valid, self.report
