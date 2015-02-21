# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import base


class StructureValidator(base.Validator):

    name = 'structure'

    def __init__(self, fail_fast=False, transform=False, report_limit=1000,
                 row_limit=30000, ignore_empty_rows=False,
                 ignore_duplicate_rows=False, ignore_defective_rows=False,
                 ignore_empty_columns=False, ignore_duplicate_columns=False,
                 ignore_headerless_columns=False, empty_strings=None,
                 report_stream=None, **kwargs):

        # TODO: `self.seen` should be maintained in a file or something
        # TODO: Check for empty columns

        super(StructureValidator, self).__init__(
            fail_fast=fail_fast, transform=transform, report_limit=report_limit,
            row_limit=row_limit, report_stream=report_stream)

        self.ignore_empty_rows = ignore_empty_rows
        self.ignore_duplicate_rows = ignore_duplicate_rows
        self.ignore_defective_rows = ignore_defective_rows
        self.ignore_empty_columns = ignore_empty_columns
        self.ignore_duplicate_columns = ignore_duplicate_columns
        self.ignore_headerless_columns = ignore_headerless_columns
        self.empty_strings = empty_strings or ('',)
        self.seen = {}

    def run_header(self, headers, header_index=0):

        valid = True

        # check for headerless columns
        if not self.ignore_headerless_columns:
            for index, header in enumerate(headers):
                if header in self.empty_strings:

                    valid = False
                    _msg = ('The header in column {0} was found '
                            'to be empty.'.format(index))
                    _type = 'Empty Header'
                    entry = self.make_entry(
                        self.RESULT_CATEGORY_HEADER,
                        self.RESULT_LEVEL_ERROR,
                        _msg,
                        _type,
                        header_index,
                        self.RESULT_HEADER_ROW_NAME,
                        index,
                        header
                    )

                    self.report.write(entry)
                    if self.fail_fast:
                        return valid, headers

        # check for duplicate columns
        if not self.ignore_duplicate_columns:
            if len(set(headers)) != len(headers):

                valid = False
                dupes = [(index, header) for index, header in
                         enumerate(headers) if
                         header.count(header) > 1]
                _type = 'Duplicate Header'

                for dupe in dupes:
                    _msg = ('The header in column {0} was found '
                            'to have duplicates.'.format(dupe[0]))
                    entry = self.make_entry(
                        self.RESULT_CATEGORY_HEADER,
                        self.RESULT_LEVEL_ERROR,
                        _msg,
                        _type,
                        header_index,
                        self.RESULT_HEADER_ROW_NAME,
                        dupe[0],
                        dupe[1]
                    )

                    self.report.write(entry)
                    if self.fail_fast:
                        return valid, headers

        return valid, headers

    def run_row(self, headers, index, row):

        valid, is_dupe, is_empty, is_defective = True, False, False, False
        row_name = self.get_row_id(row, headers)

        # check if row is duplicate
        if not self.ignore_duplicate_rows:
            _rep = hash(frozenset(row))

            if _rep in self.seen:

                self.seen[_rep].append(index)
                valid = False
                is_dupe = True
                _msg = ('Row {0} duplicates the following rows '
                        'which have already been seen: '
                        '{1}.'.format(index, self.seen[_rep]))
                _type = 'Duplicate Row'
                entry = self.make_entry(
                    self.RESULT_CATEGORY_ROW,
                    self.RESULT_LEVEL_ERROR,
                    _msg,
                    _type,
                    index,
                    row_name
                )

                self.report.write(entry)
                if self.fail_fast:
                    return valid, headers, index, row

            else:
                self.seen[_rep] = [index]

        # check if row is empty
        if not self.ignore_empty_rows:
            as_set = set(row)
            if len(as_set) == 1 and \
                    set(self.empty_strings).intersection(as_set):

                valid = False
                is_empty = True
                _msg = ('Row {0} is empty.'.format(index))
                _type = 'Empty Row'
                entry = self.make_entry(
                    self.RESULT_CATEGORY_ROW,
                    self.RESULT_LEVEL_ERROR,
                    _msg,
                    _type,
                    index,
                    row_name
                )

                self.report.write(entry)
                if self.fail_fast:
                    return valid, headers, index, row

        # check if row is defective
        if not self.ignore_defective_rows:
            if len(headers) < len(row):

                valid = False
                is_defective = True
                _msg = ('Row {0} is defective: it contains '
                        'more data than headers.'.format(index))
                _type = 'Defective Row'
                entry = self.make_entry(
                    self.RESULT_CATEGORY_ROW,
                    self.RESULT_LEVEL_ERROR,
                    _msg,
                    _type,
                    index,
                    row_name
                )

                self.report.write(entry)
                if self.fail_fast:
                    return valid, headers, index, row

            elif len(headers) < len(row):

                valid = False
                is_defective = True
                _msg = ('Row {0} is defective: it contains '
                        'less data than headers.'.format(index))
                _type = 'Defective Row'
                entry = self.make_entry(
                    self.RESULT_CATEGORY_ROW,
                    self.RESULT_LEVEL_ERROR,
                    _msg,
                    _type,
                    index,
                    row_name
                )

                self.report.write(entry)
                if self.fail_fast:
                    return valid, headers, index, row

        if self.transform and any([is_dupe, is_empty, is_defective]):
            row = None

        return valid, headers, index, row
