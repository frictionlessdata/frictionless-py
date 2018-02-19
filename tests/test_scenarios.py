# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import json
import jsonschema
import pytest
from goodtables import validate


# Tests

def test_scenarios(log, name, scenario):
    expect = list(map(lambda item: tuple(item), scenario.pop('report')))
    actual = log(validate(**scenario))
    assert actual == expect


def test_scenarios_return_valid_reports(name, scenario, report_schema):
    del scenario['report']
    report = validate(**scenario)

    jsonschema.validate(report, report_schema)


@pytest.fixture
def report_schema():
    path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'goodtables',
        'schemas',
        'report.json',
    )
    with open(path) as fp:
        yield json.load(fp)
