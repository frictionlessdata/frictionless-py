# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from goodtables import validate


# Validate

#  def test_check_file_integrity(log):
    #  source = {
        #  'resources': [
            #  {
                #  'name': 'resource1',
                #  'path': 'data/valid.csv',
                #  'bytes': 30,
                #  'hash': 'sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8',
            #  }
        #  ]
    #  }
    #  report = validate(source, checks=['file-integrity'])
    #  assert log(report) == []


#  def test_check_file_integrity_invalid_size(log):
    #  source = {
        #  'resources': [
            #  {
                #  'name': 'resource1',
                #  'path': 'data/valid.csv',
                #  'bytes': 31,
                #  'hash': 'sha256:a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8',
            #  }
        #  ]
    #  }
    #  report = validate(source, checks=['file-integrity'])
    #  assert log(report) == [
        #  (1, None, None, 'file-integrity'),
    #  ]
