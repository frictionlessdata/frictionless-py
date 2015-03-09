# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
from goodtables.pipeline import Batch
from tests import base


class TestPipeline(base.BaseTestCase):

    def setUp(self):

        super(TestPipeline, self).setUp()
        self.batch_csv =  os.path.join(self.data_dir, 'batch', 'example.csv')
        self.batch_dp = os.path.join(self.data_dir, 'batch', 'datapackage.json')

    def test_batch_from_csv(self):

        batch = Batch(self.batch_csv)
        rv = batch.run()

        self.assertTrue(rv)

    def test_batch_from_dp(self):

        batch = Batch(self.batch_dp, source_type='dp')
        rv = batch.run()

        self.assertTrue(rv)

    def test_batch_with_pipeline_post_process_handler(self):

        def say_hi(pipeline):
            return 'Hi!'

        batch = Batch(self.batch_csv, pipeline_post_process_handler=say_hi)
        rv = batch.run()

        self.assertTrue(rv)


    def test_batch_with_batch_post_processor(self):

        def say_hi(batch):
            return 'Hi!'

        batch = Batch(self.batch_csv, batch_post_process_handler=say_hi)
        rv = batch.run()

        self.assertTrue(rv)
