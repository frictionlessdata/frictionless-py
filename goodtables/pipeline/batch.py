# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import pipeline
from ..utilities import helpers
from .. import datatable


class Batch(object):

    """Run a validation pipeline batch process."""

    def __init__(self, source, source_type='csv', data_key='data',
                 schema_key='schema', pipeline_options=None,
                 post_task=None, pipeline_post_task=None):

        # `csv` and `dp` (data package) as supported source types
        # data_key is required, but schema_key is not

        self.source = source
        self.source_type = source_type
        self.data_key = data_key
        self.schema_key = schema_key
        self.dataset = self.get_dataset()
        self.pipeline_options = pipeline_options or {}
        self.post_task = post_task
        self.pipeline_post_task = pipeline_post_task
        self.pipeline = None

    def get_dataset(self):
        """Get the dataset for this batch process."""

        return getattr(self, 'get_dataset_{0}'.format(self.source_type))()

    def get_dataset_csv(self):
        """Get the dataset from a CSV file for this batch process."""

        dataset = []
        resources = datatable.DataTable(self.source)

        data_index = resources.headers.index(self.data_key)
        schema_index = None
        if self.schema_key:
            schema_index = resources.headers.index(self.schema_key)

        for entry in resources.values:

            rv = {'data': entry[data_index], 'schema': None}

            if schema_index is not None:
                rv['schema'] = entry[schema_index]

            dataset.append(rv)

        return dataset

    def get_dataset_dp(self):
        """Get the dataset from a Data Package for this batch process."""

        dataset = []
        dp = helpers.load_json_source(self.source)

        for entry in dp['resources']:
            # TODO: need to place the path inside the content of the dp: i.e.: the URL
            rv = {'data': entry['path'], 'schema': entry.get('schema')}

            dataset.append(rv)

        return dataset

    def pipeline_factory(self, data, schema):
        """Construct a pipeline."""

        options = self.pipeline_options or {}
        if options.get('schema') is None:
            options['schema'] = {}
        options['schema']['schema'] = schema

        return pipeline.Pipeline(data, options=options,
                                 post_task=self.pipeline_post_task)

    def run(self):
        """Run the batch."""

        # TODO: parallelize

        for data in self.dataset:
            pipeline = self.pipeline_factory(data['data'], data['schema'])
            pipeline.run()

        if self.post_task:
            # TODO: handle errors from here, etc.
            self.post_task(self)

        return True
