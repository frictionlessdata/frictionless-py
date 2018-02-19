# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
from goodtables.error import Error
from goodtables.spec import spec


class TestError(object):
    def test_works_with_an_custom_code(self):
        error = Error('custom-code-foobar')
        assert dict(error)['code'] == 'custom-code-foobar'

    def test_uses_error_message_defined_in_spec(self, error_code):
        expected_message = spec['errors'][error_code]['message']

        error = Error(error_code)
        assert error._message == expected_message

    def test_message_substitutes_row_and_column_numbers_by_default(self, error_code, cell):
        row_number = 51
        message = '{row_number} {column_number}'
        expected_message = message.format(
            row_number=row_number,
            column_number=cell['column-number']
        )

        error = Error(error_code, cell, row_number, message=message)

        assert error.message == expected_message

    def test_message_substitutes_extra_values(self, error_code):
        message = '{foo} {bar}'
        message_substitutions = {
            'foo': 31,
            'bar': 'foobar',
        }

        error = Error(error_code, message=message, message_substitutions=message_substitutions)

        assert error.message == '31 foobar'

    def test_to_dict(self, error_code, cell):
        row_number = 51

        error = Error(error_code, cell, row_number)

        expected_dict = {
            'code': error_code,
            'row-number': row_number,
            'column-number': cell['column-number'],
            'message': error.message,
        }
        assert dict(error) == expected_dict

    def test_sort_considers_row_first(self):
        first_error = Error('first', cell={'column-number': 10}, row_number=1)
        second_error = Error('second', cell={'column-number': 1}, row_number=10)

        assert sorted([second_error, first_error]) == [first_error, second_error]

    def test_sort_considers_columns_if_rows_are_the_same(self):
        first_error = Error('first', cell={'column-number': 1}, row_number=1)
        second_error = Error('second', cell={'column-number': 2}, row_number=1)

        assert sorted([second_error, first_error]) == [first_error, second_error]

    def test_sort_with_undefined_columns(self):
        first_error = Error('first', row_number=1)
        second_error = Error('second', row_number=2)

        assert sorted([second_error, first_error]) == [first_error, second_error]

    def test_sort_with_undefined_rows(self):
        first_error = Error('first', cell={'column-number': 1})
        second_error = Error('second', cell={'column-number': 2})

        assert sorted([second_error, first_error]) == [first_error, second_error]

    def test_sort_errors_with_undefined_rows_and_cols_should_come_first(self):
        first_error = Error('first')
        second_error = Error('second', cell={'column-number': 1}, row_number=1)

        assert sorted([second_error, first_error]) == [first_error, second_error]


@pytest.fixture
def error_code():
    return 'blank-header'


@pytest.fixture
def cell():
    return {
        'column-number': 1,
    }
