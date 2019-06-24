# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re
from copy import copy
from ..registry import check
from ..error import Error
from ..cells import create_cell


# Module API

@check('non-matching-header')
class NonMatchingHeader(object):

    # Public

    def __init__(self, order_fields=False, **options):
        self.__order_fields = order_fields

    def check_headers(self, cells, sample=None):
        if self.__order_fields:
            return _check_with_ordering(cells)
        else:
            return _check_without_ordering(cells)


# Internal


def _check_with_ordering(cells):
    # Update fields order to maximally match headers order
    headers = [cell.get('header') for cell in cells]
    new_headers = []
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
                        field_name = _get_field_name(cells[index])

        field_name = _get_field_name(cells[index])
        if _slugify(header) != _slugify(field_name):
            # Cell header and field_name are still different
            # which means there is no matching field for the header.
            # Add a new cell with an empty header so that the missing-header
            # error will be thrown later.
            new_cell = create_cell(header=None, field=cell.get('field'))
            new_headers.append(new_cell)
            # Change the current cell's field to None
            cell['field'] = None

    # Add the new headers
    cells.extend(new_headers)

    # Run check with no field ordering
    return _check_without_ordering(cells)


def _check_without_ordering(cells):
    errors = []

    for cell in copy(cells):
        if cell.get('field') is not None:
            header = cell.get('header')
            if header != cell['field'].name and header is not None:
                # Add error
                message_substitutions = {
                    'field_name': '"{}"'.format(cell['field'].name),
                    'header': '"{}"'.format(cell.get('header')),
                }
                error = Error(
                    'non-matching-header',
                    cell,
                    message_substitutions=message_substitutions
                )
                errors.append(error)
                if _slugify(header) != _slugify(cell['field'].name):
                    # Remove cell
                    cells.remove(cell)

    return errors


def _get_field_name(cell):
    if cell.get('field'):
        return cell['field'].name


def _slugify(string):
    if string is None:
        return None
    string = re.sub(r'[\W_]+', '', string)
    string = string.lower()
    return string


def _swap_fields(cell1, cell2):
    field1 = cell1.get('field', None)
    cell1['field'] = cell2.get('field', None)
    cell2['field'] = field1
