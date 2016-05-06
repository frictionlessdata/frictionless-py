# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import time
from . import pipeline
from ..utilities import helpers
from .. import datatable


class Batch(object):

    """Run a pipeline batch process.

    Args:
    * `source`: path to the source file
    * `source_type`: 'csv' or 'datapackage'
    * `data_key`: The key for the data (only used when source_type is 'csv')
    * `schema_key`: The key for the schema (only used when source_type is 'csv').
    * `sleep`:  The time (in seconds) to wait beteween pipelines
    * `pipeline_options`: Options to pass to each pipeline instance.
    * `post_task`: Task handler to run after all pipelines have run.
    * `pipeline_post_task`: Task handler passed to each pipeline instance.

    """

    def __init__(self, source, source_type='csv', sleep=None, data_key='data', 
                 schema_key='schema', format_key='format', encoding_key='encoding',
                 pipeline_options=None, post_task=None, pipeline_post_task=None):

        self.source = source
        self.source_type = source_type
        self.data_key = data_key
        self.schema_key = schema_key
        self.format_key = format_key
        self.encoding_key = encoding_key
        self.dataset = self.get_dataset()
        self.pipeline_options = pipeline_options or {}
        self.current_pipeline = None
        self.reports = []

        helpers.validate_handler(post_task, 1)
        helpers.validate_handler(pipeline_post_task, 1)

        self.post_task = post_task
        self.pipeline_post_task = pipeline_post_task

        if sleep and not isinstance(sleep, (int, float)):
            raise ValueError('Received non int or float for the \'sleep\' argument.')
        self.sleep = sleep

    def get_dataset(self):
        """Get the dataset for this batch process."""

        return getattr(self, 'get_dataset_{0}'.format(self.source_type))()

    def get_dataset_csv(self):
        """Get the dataset from a CSV file for this batch process."""

        dataset = []
        resources = datatable.DataTable(self.source, encoding='utf-8')

        data_index = resources.headers.index(self.data_key)
        keys_header_index = {}
        
        for key in [self.schema_key, self.format_key, self.encoding_key]:
            if key in resources.headers:
                keys_header_index[key] = resources.headers.index(key)

        for entry in resources.values:

            rv = {'data': entry[data_index], 'schema': None, 'encoding': None,
                  'format': None}
            
            for key, index in keys_header_index.items():
                if index is not None:
                    rv[key] = entry[index]

            dataset.append(rv)

        return dataset

    def get_dataset_datapackage(self):
        """Get the dataset from a Data Package for this batch process."""

        _name = 'datapackage.json'
        descriptor = os.path.join(self.source, _name)
        dataset = []
        # TODO: We want to use https://github.com/tryggvib/datapackage here
        # but, in order to do so, we need these issues resolved:
        # https://github.com/tryggvib/datapackage/issues/35
        # https://github.com/tryggvib/datapackage/issues/33
        pkg = helpers.load_json_source(descriptor)
        for entry in pkg['resources']:

            if entry.get('url'):
                data = entry['url']
            elif entry.get('path'):
                if pkg.get('base'):
                    data = '{0}{1}'.format(pkg['base'], entry['path'])
                else:
                    data = os.path.join(self.source, entry['path'])
            else:
                data = entry.get('data')

            dataset.append({
                'data': data,
                'schema': entry.get('schema')
            })

        return dataset

    def pipeline_factory(self, data, schema, format, encoding):
        """Construct a pipeline."""

        options = self.pipeline_options or {}
        if options.get('options') is None:
            options['options'] = {}
            
        if schema is not None:
            if options['options'].get('schema') is None:
                options['options']['schema'] = {}

            options['options']['schema']['schema'] = schema
            
        if encoding: options['encoding'] = encoding
        if format:   options['format'] = format

        return pipeline.Pipeline(data, post_task=self.pipeline_post_task,
                                 **options)

    def run(self):
        """Run the batch."""

        # TODO: parallelize

        for data in self.dataset:
            pipeline = self.pipeline_factory(data=data['data'],
                                             schema=data['schema'],
                                             format=data['format'], 
                                             encoding=data['encoding'])
            self.current_pipeline = pipeline
            result, report = self.current_pipeline.run()
            self.reports.append(report)
            
            if self.sleep:
                time.sleep(self.sleep)

        if self.post_task:
            self.post_task(self)

        return not any([report.count for report in self.reports])
