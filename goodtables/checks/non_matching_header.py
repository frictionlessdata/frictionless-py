# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re
from copy import copy
from ..spec import spec
from ..registry import check


# Module API

@check('non-matching-header', type='schema', context='head')
class NonMatchingHeader(object):

    # Public

    def __init__(self, order_fields=False, **options):
        self.__order_fields = order_fields

    def check_headers(self, errors, cells, sample=None):
        if self.__order_fields:
            _check_with_ordering(errors, cells)
        else:
            _check_without_ordering(errors, cells)


# Internal


def _check_with_ordering(errors, cells):
    # Update fields order to maximally match headers order
    headers = [cell.get('header') for cell in cells]
    for index, header in enumerate(headers):
        if header is None:
            continue
        field_name = _get_field_name(cells[index])
        # Cell header and field_name are different
        if _slugify(header) != _slugify(field_name):
            # If there is the match in next cells - swap fields
            for cell in cells[index+1:]:
                # We've found field matching given header
                if _slugify(header) == _slugify(_get_field_name(cell)):
                    _swap_fields(cells[index], cell)
                    break
                if field_name:
                    # Given field matches some header also swap
                    if _slugify(field_name) == _slugify(cell.get('header')):
                        _swap_fields(cells[index], cell)
    # Run check with no field ordering
    _check_without_ordering(errors, cells)


def _check_without_ordering(errors, cells):
    for cell in copy(cells):
        if set(cell).issuperset(['number', 'header', 'field']):
            if cell['header'] != cell['field'].name:
                # Add error
                message = spec['errors']['non-matching-header']['message']
                message = message.format(
                    column_number=cell['number'],
                    field_name='"%s"' % cell['field'].name)
                errors.append({
                    'code': 'non-matching-header',
                    'message': message,
                    'row-number': None,
                    'column-number': cell['number'],
                })
                if _slugify(cell['header']) != _slugify(cell['field'].name):
                    # Remove cell
                    cells.remove(cell)


def _get_field_name(cell):
    field_name = None
    if 'field' in cell:
        field_name = cell['field'].name
    return field_name


def _slugify(string):
    if string is None:
        return None
    string = re.sub(r'[\W_]+', '', string)
    string = string.lower()
    return string


def _swap_fields(cell1, cell2):
    field1 = cell1.get('field')
    cell1['field'] = cell2.get('field')
    cell2['field'] = field1
    if cell1['field'] is None:
        del cell1['field']
    if cell2['field'] is None:
        del cell2['field']
