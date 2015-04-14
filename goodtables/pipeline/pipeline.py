# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import importlib
import shutil
import tempfile
import json
import csv
import decimal
import tellme
from ..utilities import data_package, csv_dialect, helpers
from .. import datatable
from .. import exceptions
from .. import compat


class Pipeline(object):

    """Validate a (tabular) data source through a validation pipeline.

    Args:
    * processors: A list of processor names to process `data_source`
        * Each name can be a 'shortname' for the default processors
            * e.g., ['structure', 'schema']
        * Each name can be a string path to a processor
            * e.g., ['custompackage.CustomValidator', 'schema']
            * Custom processors must implement the Validator API
    * data: A buffer, filepath, string or URL to the table data
    * format: The format of `data_source`. 'csv' or 'json'
    * dialect: A buffer, filepath, string or URL to a CSV dialect spec
    * options: a dict configuration object for the pipeline
        * Each processor has its options nested under its 'shortname'
        * Custom processors have options nested under cls.__name__.lower()
        * e.g.:
            {'structure': {#options}, 'customprocessor': {#options}}
    * workspace: path to directory for files. e.g.: '/my/path'
    * dry_run: No files are persisted after the run has been completed

    Returns:
        A tuple of `valid, report`, where `valid` is a boolean expressing
        validity according to the whole pipeline, and report is a dict
        of the entire pipeline report where each top-level key matches
        a processor in the pipeline.

    """

    ROW_LIMIT_MAX = 30000
    REPORT_LIMIT_MAX = 1000
    SOURCE_FILENAME = 'source.csv'
    TRANSFORM_FILENAME = 'transform.csv'
    DIALECT_FILENAME = 'dialect.json'
    DATA_FORMATS = ('csv', 'excel', 'json')

    def __init__(self, data, processors=None, dialect=None, format='csv',
                 encoding=None, options=None, workspace=None, dry_run=True,
                 transform=True, fail_fast=False, row_limit=20000,
                 report_limit=1000, report_stream=None, header_index=0,
                 break_on_invalid_processor=True, post_task=None,
                 report_post_task=None):

        if data is None:
            _msg = '`data` must be a filepath, url or stream.'
            raise exceptions.PipelineBuildError(_msg)

        self.openfiles = []
        self.processors = processors or helpers.DEFAULT_PIPELINE
        self.dialect = self.get_dialect(dialect)
        self.format = format
        self.encoding = encoding
        self.options = options or {}
        self.dry_run = dry_run
        self.workspace = self.get_workspace(workspace)
        self.transform = transform
        self.fail_fast = fail_fast
        self.row_limit = self.get_row_limit(row_limit)
        self.report_limit = self.get_report_limit(report_limit)
        self.report_stream = report_stream
        self.header_index = header_index
        self.break_on_invalid_processor = break_on_invalid_processor

        helpers.validate_handler(report_post_task)
        helpers.validate_handler(post_task)

        self.report_post_task = report_post_task or helpers.pipeline_stats
        self.post_task = post_task

        if self.report_stream:
            report_stream_tests = [isinstance(self.report_stream, io.TextIOBase),
                                   self.report_stream.writable(),
                                   self.report_stream.seekable()]

            if not all(report_stream_tests):
                _msg = '`report_stream` must be a seekable and writable text stream.'
                raise exceptions.PipelineBuildError(_msg)

            report_backend = 'client'
        else:
            report_backend = 'yaml'

        report_options = {
            'schema': helpers.report_schema,
            'backend': report_backend,
            'client_stream': self.report_stream,
            'limit': self.report_limit,
            'post_task': self.report_post_task
        }

        self.report = tellme.Report('Pipeline', **report_options)

        self.pipeline = self.get_pipeline()

        try:
            self.data = datatable.DataTable(data, format=self.format,
                                            encoding=encoding,
                                            header_index=self.header_index)
        except datatable.DataTable.RAISES as e:
            raise exceptions.PipelineBuildError(e.msg)

        self.openfiles.extend(self.data.openfiles)

        if not self.dry_run:
            self.init_workspace()

    def init_workspace(self):
        """Initalize the workspace for this run."""

        self.create_file(self.data.stream, self.SOURCE_FILENAME, self.data.headers)
        self.create_file('', self.TRANSFORM_FILENAME)
        self.create_file(json.dumps(self.dialect), self.DIALECT_FILENAME)

    def get_workspace(self, filepath):
        """Return a workspace for this run."""
        # TODO: use pudo/barn

        if not self.dry_run:
            return filepath or tempfile.mkdtemp()

        return None

    def get_pipeline(self):
        """Get the pipeline for this instance."""

        pipeline = []
        for name in self.processors:
            _class = self.resolve_processor(name)
            options = self.options.get(_class.name, {})
            # override options with those we accept directly from the pipeline
            options['row_limit'] = self.row_limit
            options['report_limit'] = self.report_limit
            options['report_stream'] = self.report_stream
            options['transform'] = self.transform
            options['fail_fast'] = self.fail_fast
            options['header_index'] = self.header_index
            options['report'] = self.report

            try:
                instance = _class(**options)
                pipeline.append(instance)
            except _class.RAISES as e:
                raise exceptions.PipelineBuildError(e.msg)

        return pipeline

    def get_dialect(self, dialect_source):
        """Get a CSV dialect instance for this data."""

        if dialect_source:
            _valid, rv = csv_dialect.validate(dialect_source)
            if not _valid:
                raise exceptions.InvalidSpec
            return rv
        else:
            return None

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

    def create_file(self, data, name, headers=None):
        """Create a file in the pipeline workspace."""

        filepath = os.path.join(self.workspace, name)
        with io.open(filepath, mode='w+t', encoding='utf-8') as destfile:
            if headers:
                destfile.write(','.join(headers))

            if isinstance(data, compat.str):
                destfile.write(data)
            elif isinstance(data, compat.bytes):
                # TODO: We should not ever deal with bytes here: see why we are (or if we still are)
                destfile.write(data.decode('utf-8'))
            else:
                destfile.write(data.read())
                data.seek(0)

    def resolve_processor(self, processor_name):
        """Return a processor class."""

        if processor_name in helpers.builtin_processors():
            processor_class = helpers.builtin_processors()[processor_name]
        else:
            # resolve a custom processor
            _module, _class = processor_name.rsplit('.', 1)
            try:
                processor_class = getattr(importlib.import_module(_module),
                                          _class)
            except ImportError as e:
                # TODO: something better here
                raise e

        return processor_class

    def register_processor(self, processor_name, options=None, position=None):
        """Register a processor on the pipeline."""

        processor_class = self.resolve_processor(processor_name)
        options = options or {}
        processor = processor_class(**options)

        if position is None:
            self.pipeline.append(processor)
        else:
            self.pipeline.insert(position, processor)

    def run(self):
        """Run the pipeline."""

        def _run_valid(process_valid, run_valid):
            """Set/maintain the valid state of the run."""
            if not process_valid and run_valid:
                return False
            return run_valid

        valid = True

        for processor in self.pipeline:

            _valid, _, self.data = processor.run(self.data, is_table=True)
            valid = _run_valid(_valid, valid)

            # if a validator returns invalid, we stop the pipeline,
            # unless break_on_invalid_processor is False
            if not valid and self.break_on_invalid_processor:
                break

            if not self.dry_run and self.transform:
                # TODO: do what we'll do with transform data, workspace, etc.
                pass
            else:
                self.data.replay()

        self.set_report_meta()

        if self.post_task:
            # TODO: handle what happens in here
            self.post_task(self)

        return valid, self.report

    def rm_workspace(self):
        """Remove this run's workspace from disk."""

        return shutil.rmtree(self.workspace)

    def set_report_meta(self):
        """Set information and statistics for this run on report['meta']."""
        self.report.meta['row_count'] = self.pipeline[0].row_count or 1
        self.report.meta['header_index'] = self.header_index
        self.report.meta['headers'] = self.data.headers
