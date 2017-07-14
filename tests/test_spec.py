# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import json
import pytest
import requests
from goodtables.spec import spec


# Tests

def test_spec_is_up_to_date():
    origin_spec = requests.get('https://raw.githubusercontent.com/frictionlessdata/data-quality-spec/master/spec.json').json()
    assert spec == origin_spec, 'run `make spec` to update the spec'
