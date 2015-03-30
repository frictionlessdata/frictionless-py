# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
from goodtables.pipeline import Batch
from goodtables import exceptions
from tests import base


class TestPipeline(base.BaseTestCase):

    def setUp(self):

        super(TestPipeline, self).setUp()
        self.batch_csv = os.path.join(self.data_dir, 'batch', 'example.csv')
        self.batch_datapackage = os.path.join(self.data_dir, 'batch', 'datapackage')

    def test_batch_from_csv(self):

        batch = Batch(self.batch_csv)

        self.assertEqual(len(batch.dataset), 3)

    def test_batch_from_datapackage(self):

        batch = Batch(self.batch_datapackage, source_type='datapackage')

        self.assertEqual(len(batch.dataset), 1)

    def test_batch_with_pipeline_post_process_handler(self):

        def say_hi(pipeline):
            return 'Hi!'

        batch = Batch(self.batch_csv, pipeline_post_task=say_hi)
        rv = batch.run()

        self.assertFalse(rv)


    def test_batch_with_batch_post_processor(self):

        def say_hi(batch):
            return 'Hi!'

        batch = Batch(self.batch_csv, post_task=say_hi)
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
