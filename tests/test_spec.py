# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import json
import requests


def test_spec_is_up_to_date():
    actual = json.load(io.open('goodtables/spec.json', encoding='utf-8'))
    expect = requests.get('https://raw.githubusercontent.com/frictionlessdata/data-quality-spec/master/spec.json').json()
    assert actual == expect, 'run `make spec` to update the spec'
