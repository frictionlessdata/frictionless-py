# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from timeit import default_timer as timer

from goodtables.pipeline import Batch
from goodtables import exceptions
from tests import base


class TestPipeline(base.BaseTestCase):

    def setUp(self):

        super(TestPipeline, self).setUp()
        self.batch_csv = os.path.join(self.data_dir, 'batch', 'example.csv')
        self.pipeline_options = {'processors': ['schema', 'structure']}
        self.batch_datapackage = os.path.join(self.data_dir, 'batch', 'datapackage')

    def test_batch_from_csv(self):

        batch = Batch(self.batch_csv, pipeline_options=self.pipeline_options)

        self.assertEqual(len(batch.dataset), 4)

    def test_batch_from_datapackage(self):

        batch = Batch(self.batch_datapackage, source_type='datapackage')

        self.assertEqual(len(batch.dataset), 1)

    def test_batch_with_pipeline_post_process_handler(self):

        def say_hi(pipeline):
            return 'Hi!'

        batch = Batch(self.batch_csv, pipeline_post_task=say_hi,
                      pipeline_options=self.pipeline_options)
        rv = batch.run()

        self.assertFalse(rv)

    def test_batch_with_batch_post_processor(self):

        def say_hi(batch):
            return 'Hi!'

        batch = Batch(self.batch_csv, post_task=say_hi,
                      pipeline_options=self.pipeline_options)
        rv = batch.run()

        self.assertFalse(rv)

    def test_bad_post_task_raises(self):

        say_hi = 'Say Hi!'
        self.assertRaises(exceptions.InvalidHandlerError, Batch,
                          self.batch_csv, post_task=say_hi)

    def test_bad_pipeline_post_task_raises(self):

        say_hi = 'Say Hi!'
        self.assertRaises(exceptions.InvalidHandlerError, Batch,
                          self.batch_csv, pipeline_post_task=say_hi)

    def test_batch_with_batch_sleep_time(self):

        def default_time():
            batch = Batch(self.batch_csv, pipeline_options=self.pipeline_options)
            start = timer(); batch.run(); end = timer()
            return end - start

        def custom_sleep_time():
            batch = Batch(self.batch_csv, sleep=3, pipeline_options=self.pipeline_options)
            start = timer(); batch.run(); end = timer()
            return end - start

        self.assertTrue(default_time() < custom_sleep_time())
