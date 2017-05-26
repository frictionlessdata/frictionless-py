# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re
from copy import copy
from ..spec import spec
from ..decorators import check


# Module API

@check('non-matching-header')
def non_matching_header(errors, columns, sample=None, order_fields=False):

    # No field ordering
    if not order_fields:
        for column in copy(columns):
            if len(column) == 3:
                if column['header'] != column['field'].name:
                    # Add error
                    message = spec['errors']['non-matching-header']['message']
                    message = message.format(
                        column_number=column['number'],
                        field_name=column['field'].name)
                    errors.append({
                        'code': 'non-matching-header',
                        'message': message,
                        'row-number': None,
                        'column-number': column['number'],
                    })
                    if _slugify(column['header']) != _slugify(column['field'].name):
                        # Remove column
                        columns.remove(column)

    # Field ordering
    else:
        # Update fields order to maximally match headers order
        headers = [column.get('header') for column in columns]
        for index, header in enumerate(headers):
            if header is None:
                continue
            field_name = _get_field_name(columns[index])
            # Column header and field_name are different
            if _slugify(header) != _slugify(field_name):
                # If there is the match in next columns - swap fields
                for column in columns[index+1:]:
                    # We've found field matching given header
                    if _slugify(header) == _slugify(_get_field_name(column)):
                        _swap_fields(columns[index], column)
                        break
                    if field_name:
                        # Given field matches some header also swap
                        if _slugify(field_name) == _slugify(column.get('header')):
                            _swap_fields(columns[index], column)
        # Run check with no field ordering
        non_matching_header(errors, columns)


# Internal


def _get_field_name(column):
    field_name = None
    if 'field' in column:
        field_name = column['field'].name
    return field_name


def _slugify(string):
    if string is None:
        return None
    string = re.sub(r'[\W_]+', '', string)
    string = string.lower()
    return string


def _swap_fields(column1, column2):
    field1 = column1.get('field')
    column1['field'] = column2.get('field')
    column2['field'] = field1
    if column1['field'] is None:
        del column1['field']
    if column2['field'] is None:
        del column2['field']
