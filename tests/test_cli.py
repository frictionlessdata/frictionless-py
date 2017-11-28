# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

try:
    import unittest.mock as mock
except ImportError:
    import mock
from click.testing import CliRunner
from goodtables.cli import cli


# Tests

def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert len(result.output.split('.')) == 3


@mock.patch('goodtables.validate', autospec=True)
def test_cli_infer_schema_enables_infer_fields(validate_mock):
    CliRunner().invoke(cli, ['--infer-schema', 'data.csv'])

    last_call_args = validate_mock.call_args
    assert last_call_args is not None
    assert last_call_args[-1].get('infer_schema')
    assert last_call_args[-1].get('infer_fields')
