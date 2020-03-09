# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import functools
from .spec import spec


@functools.total_ordering
class Error(object):
    """Describes a validation check error

    # Arguments
        code (str): The error code. Must be one in the spec.
        cell (dict, optional): The cell where the error occurred.
        row_number (int, optional): The row number where the error occurs.
        message (str, optional):
            The error message. Defaults to the message from the Data Quality Spec.
        message_substitutions (dict, optional):
            Dictionary with substitutions to be used when
            generating the error message and description.

    # Raises
        KeyError: Raised if the error code isn't known.

    """

    def __init__(
        self,
        code,
        cell=None,
        row_number=None,
        message=None,
        message_substitutions=None
    ):
        self._spec = spec['errors'].get(code)
        default_message = None
        if self._spec:
            default_message = self._spec['message']

        self._code = code
        self._cell = cell or {}
        self._row = None
        self._row_number = row_number or self._cell.get('row-number')
        self._message = message or default_message
        self._message_substitutions = message_substitutions or {}

    def __iter__(self):
        for key, value in self._to_dict().items():
            yield (key, value)

    @property
    def cell(self):
        return self._cell

    @property
    def code(self):
        return self._code

    @property
    def row_number(self):
        return self._row_number

    @property
    def column_number(self):
        return self._cell.get('column-number')

    @property
    def message(self):
        if self._message:
            return self._message.format(
                row_number=self.row_number,
                column_number=self.column_number,
                **self._message_substitutions
            )

    @property
    def description(self):
        # TODO: Add string substitutions
        if self._spec:
            return self._spec['description']

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, value):
        self._row = value

    def __eq__(self, other):
        my_row = self.row_number or 0
        my_col = self.column_number or 0
        other_row = other.row_number or 0
        other_col = other.column_number or 0

        return (my_row == other_row) and (my_col == other_col)

    def __lt__(self, other):
        my_row = self.row_number or 0
        my_col = self.column_number or 0
        other_row = other.row_number or 0
        other_col = other.column_number or 0

        return (my_row < other_row) or (my_row == other_row and my_col < other_col)

    def _to_dict(self):
        return {
            'code': self.code,
            # TODO: it's a hack; reimplement using head/body context
            'row': self.row if self.code != 'source-error' else None,
            'row-number': self.row_number,
            'column-number': self.column_number,
            'message': self.message,
            'message-data': {k: v.strip('"') if isinstance(v, str) else v for k, v
                             in self._message_substitutions.items()},
        }
