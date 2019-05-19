# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tableschema import Field
from goodtables.checks.non_matching_header import NonMatchingHeader
import goodtables.cells


# Check

def test_check_non_matching_header(log):
    cells = [
        goodtables.cells.create_cell('name1', field=Field({'name': 'name1'}), column_number=1),
        goodtables.cells.create_cell('name2', field=Field({'name': 'name2'}), column_number=2),
        goodtables.cells.create_cell('name3', column_number=3),
    ]
    non_matching_header = NonMatchingHeader()
    errors = non_matching_header.check_headers(cells)
    assert log(errors) == []
    assert len(cells) == 3


def test_check_non_matching_header_problem(log):
    cells = [
        goodtables.cells.create_cell('name1', field=Field({'name': 'name2'}), column_number=1),
        goodtables.cells.create_cell('name2', field=Field({'name': 'name1'}), column_number=2),
        goodtables.cells.create_cell('name3', column_number=3),
    ]
    non_matching_header = NonMatchingHeader()
    errors = non_matching_header.check_headers(cells)
    assert log(errors) == [
        (None, 1, 'non-matching-header'),
        (None, 2, 'non-matching-header'),
    ]
    assert len(cells) == 1


def test_check_non_matching_header_order_fields(log):
    cells = [
        goodtables.cells.create_cell('name1', field=Field({'name': 'name2'}), column_number=1),
        goodtables.cells.create_cell('name2', field=Field({'name': 'name1'}), column_number=2),
        goodtables.cells.create_cell('name3', column_number=3),
    ]
    non_matching_header = NonMatchingHeader(order_fields=True)
    errors = non_matching_header.check_headers(cells)
    assert log(errors) == []
    # A new header cell will be added by the non-matching-header check because
    # there is no field for the "name3" header
    assert len(cells) == 4


def test_check_non_matching_header_order_fields_problem(log):
    cells = [
        goodtables.cells.create_cell('name1', field=Field({'name': 'name4'}), column_number=1),
        goodtables.cells.create_cell('name2', field=Field({'name': 'name1'}), column_number=2),
        goodtables.cells.create_cell('name3', column_number=3),
    ]
    non_matching_header = NonMatchingHeader(order_fields=True)
    errors = non_matching_header.check_headers(cells)
    assert log(errors) == [
        (None, 2, 'non-matching-header'),
    ]
    # New header cells will be added by the non-matching-header check because
    # there are no fields for the "name2" and "name3" headers
    assert len(cells) == 4


def test_check_non_matching_header_with_empty_header_name(log):
    # When the header is None, it means there's a missing header.
    cells = [
        goodtables.cells.create_cell(None, field=Field({'name': 'name3'}), column_number=1),
    ]
    non_matching_header = NonMatchingHeader(order_fields=True)
    errors = non_matching_header.check_headers(cells)
    assert log(errors) == []
    assert len(cells) == 1
