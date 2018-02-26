# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from tableschema import Field
from goodtables.checks.required_constraint import required_constraint
import goodtables.cells


def test_check_required_constraint(log):
    cell = goodtables.cells.create_cell(
        'id',
        '',
        field=Field({
            'name': 'id',
            'constraints': {
                'required': True,
            }
        })
    )
    errors = required_constraint([cell])
    assert len(errors) == 1
    assert errors[0].code == 'required-constraint'


def test_primary_key_fields_are_required_by_default(log):
    cell = goodtables.cells.create_cell(
        'id',
        '',
        field=Field({
            'name': 'id',
            'primaryKey': True,
        })
    )
    errors = required_constraint([cell])
    assert len(errors) == 1
    assert errors[0].code == 'required-constraint'


def test_primary_keys_required_constraint_can_be_overloaded(log):
    cell = goodtables.cells.create_cell(
        'id',
        '',
        field=Field({
            'name': 'id',
            'constraints': {
                'required': False,
            },
            'primaryKey': True,
        })
    )
    errors = required_constraint([cell])
    assert not errors
