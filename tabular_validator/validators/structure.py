# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import base


class StructureValidator(base.Validator):

    name = 'structure'

    def __init__(self, fail_fast=False, transform=False, report_limit=1000,
                 ignore_empty_rows=False, ignore_duplicate_rows=False,
                 ignore_defective_rows=False, ignore_empty_columns=False,
                 ignore_duplicate_columns=False,
                 ignore_headerless_columns=False, empty_strings=None):

        # TODO: `self.seen` should be maintained in a file or something
        # TODO: Check for empty columns

        super(StructureValidator, self).__init__(fail_fast=fail_fast,
                                                 transform=transform,
                                                 report_limit=report_limit)

        self.ignore_empty_rows = ignore_empty_rows
        self.ignore_duplicate_rows = ignore_duplicate_rows
        self.ignore_defective_rows = ignore_defective_rows
        self.ignore_empty_columns = ignore_empty_columns
        self.ignore_duplicate_columns = ignore_duplicate_columns
        self.ignore_headerless_columns = ignore_headerless_columns
        self.empty_strings = empty_strings or ('',)
        self.seen = {}

    def run_header(self, headers):

        valid = True

        # check for headerless columns
        if not self.ignore_headerless_columns:
            for index, header in enumerate(headers):
                if header in self.empty_strings:
                    valid = False
                    self.report.write({
                        'name': 'Empty Header',
                        'category': 'headers',
                        'level': 'error',
                        'position': index,
                        'message': ('The header at position {0} was found '
                                    'to be empty.'.format(index))
                    })

        # check for duplicate columns
        if not self.ignore_duplicate_columns:
            if len(set(headers)) != len(headers):
                valid = False
                dupes = [(index, header) for index, header in
                         enumerate(headers) if
                         header.count(header) > 1]
                for dupe in dupes:
                    self.report.write({
                        'name': 'Duplicate Header',
                        'category': 'headers',
                        'level': 'error',
                        'position': dupe[0],
                        'message': ('The header at position {0} was found '
                                    'to have duplicates.'.format(dupe[0]))
                    })

        if self.transform:
            for index, header in enumerate(headers):
                if header in self.empty_strings:
                    headers[index] = None

        return valid, headers

    def run_row(self, headers, index, row):

        valid, is_dupe, is_empty, is_defective = True, False, False, False

        # check if row is duplicate
        if not self.ignore_duplicate_rows:
            _rep = hash(frozenset(row))
            if _rep in self.seen:
                self.seen[_rep].append(index)
                valid = False
                is_dupe = True
                self.report.write({
                    'name': 'Duplicate Row',
                    'category': 'rows',
                    'level': 'error',
                    'position': index,
                    'message': 'Row {0} duplicates rows {1}'.format(
                        index, self.seen[_rep])
                })
            else:
                self.seen[_rep] = [index]

        # check if row is empty
        if not self.ignore_empty_rows:
            as_set = set(row)
            if len(as_set) == 1 and \
                    set(self.empty_strings).intersection(as_set):
                valid = False
                is_empty = True
                self.report.write({
                    'name': 'Empty Row',
                    'category': 'rows',
                    'level': 'error',
                    'position': index,
                    'message': 'Row {0} is empty'.format(index)
                })

        # check if row is defective
        if not self.ignore_defective_rows:
            if len(headers) < len(row):
                valid = False
                is_defective = True
                self.report.write({
                    'name': 'Defective Row',
                    'category': 'rows',
                    'level': 'error',
                    'position': index,
                    'message': ('Row {0} is defective '
                                '(more data than headers)'.format(index))
                })

            elif len(headers) < len(row):
                valid = False
                is_defective = True
                self.report.write({
                    'name': 'Defective Row',
                    'category': 'rows',
                    'level': 'error',
                    'position': index,
                    'message': ('Row {0} is defective '
                                '(less data than headers)'.format(index))
                })

        if self.transform and any([is_dupe, is_empty, is_defective]):
            row = None

        return valid, headers, index, row
