# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import base


RESULTS = {
    'structure_001': {
        'id': 'structure_001',
        'name': 'Missing Header',
        'msg': 'Header column number {0} is empty.',
        'help': '',
        'help_edit': ''
    },
    'structure_002': {
        'id': 'structure_002',
        'name': 'Duplicate Header',
        'msg': 'The header column \"{0}\" is duplicated.',
        'help': '',
        'help_edit': ''
    },
    'structure_003': {
        'id': 'structure_003',
        'name': 'Defective Row',
        'msg': 'The row dimensions are incorrect compared to headers.',
        'help': '',
        'help_edit': ''
    },
    'structure_004': {
        'id': 'structure_004',
        'name': 'Duplicate Row',
        'msg': 'The exact same row has been seen before (a duplicate).',
        'help': '',
        'help_edit': ''
    },
    'structure_005': {
        'id': 'structure_005',
        'name': 'Empty Row',
        'msg': 'Row is empty.',
        'help': '',
        'help_edit': ''
    }
}


class StructureProcessor(base.Processor):

    name = 'structure'
    RESULT_TYPES = RESULTS
    
    def __init__(self, fail_fast=False, transform=False, report_limit=1000,
                 row_limit=30000, ignore_empty_rows=False,
                 ignore_duplicate_rows=False, ignore_defective_rows=False,
                 ignore_empty_columns=False, ignore_duplicate_columns=False,
                 ignore_headerless_columns=False, empty_strings=None,
                 report_stream=None, report=None, result_level='error',
                 **kwargs):

        # TODO: `self.seen` should be maintained in a file or something
        # TODO: Check for empty columns

        super(StructureProcessor, self).__init__(
            fail_fast=fail_fast, transform=transform, report_limit=report_limit,
            row_limit=row_limit, report_stream=report_stream, report=report,
            result_level=result_level)

        self.ignore_empty_rows = ignore_empty_rows
        self.ignore_duplicate_rows = ignore_duplicate_rows
        self.ignore_defective_rows = ignore_defective_rows
        self.ignore_empty_columns = ignore_empty_columns
        self.ignore_duplicate_columns = ignore_duplicate_columns
        self.ignore_headerless_columns = ignore_headerless_columns
        if empty_strings:
            self.empty_strings = frozenset(empty_strings)
        else:
            self.empty_strings = frozenset([''])
        self.seen = {}
        self._repempty = frozenset([''])

    def run_header(self, headers, header_index=0):

        valid = True

        # check for headerless columns
        if not self.ignore_headerless_columns:
            for index, header in enumerate(headers):
                if header in self.empty_strings:

                    valid = False
                    _type = RESULTS['structure_001']
                    entry = self.make_entry(
                        self.name,
                        self.RESULT_CATEGORY_HEADER,
                        self.RESULT_LEVEL_ERROR,
                        _type['msg'].format(index),
                        _type['id'],
                        _type['name'],
                        headers,
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
                         headers.count(header) > 1]
                _type = RESULTS['structure_002']

                for dupe in dupes:
                    entry = self.make_entry(
                        self.name,
                        self.RESULT_CATEGORY_HEADER,
                        self.RESULT_LEVEL_ERROR,
                        _type['msg'].format(dupe[1]),
                        _type['id'],
                        _type['name'],
                        headers,
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
        _repset = frozenset(row)
        _rephash = hash(_repset)

        # check if row is duplicate
        if not self.ignore_duplicate_rows:

            if _rephash in self.seen:

                # don't keep writing results for totally empty rows
                if _repset == self._repempty:
                    pass
                else:
                    previous_instances = list(self.seen[_rephash])
                    self.seen[_rephash].append(index)
                    valid = False
                    is_dupe = True
                    _type = RESULTS['structure_004']
                    entry = self.make_entry(
                        self.name,
                        self.RESULT_CATEGORY_ROW,
                        self.RESULT_LEVEL_ERROR,
                        _type['msg'],
                        _type['id'],
                        _type['name'],
                        row,
                        index,
                        row_name
                    )

                    self.report.write(entry)
                    if self.fail_fast:
                        return valid, headers, index, row

            else:
                self.seen[_rephash] = [index]

        # check if row is empty
        if not self.ignore_empty_rows:
            if len(_repset) == 1 and ((_repset == self._repempty) or \
                                      self.empty_strings.intersection(_repset)):

                valid = False
                is_empty = True
                _type = RESULTS['structure_005']
                entry = self.make_entry(
                    self.name,
                    self.RESULT_CATEGORY_ROW,
                    self.RESULT_LEVEL_ERROR,
                    _type['msg'],
                    _type['id'],
                    _type['name'],
                    row,
                    index,
                    row_name
                )

                self.report.write(entry)
                if self.fail_fast:
                    return valid, headers, index, row

        # check if row is defective
        if not self.ignore_defective_rows:
            if len(headers) != len(row):

                valid = False
                is_defective = True
                _type = RESULTS['structure_003']
                entry = self.make_entry(
                    self.name,
                    self.RESULT_CATEGORY_ROW,
                    self.RESULT_LEVEL_ERROR,
                    _type['msg'],
                    _type['id'],
                    _type['name'],
                    row,
                    index,
                    row_name
                )

                self.report.write(entry)
                if self.fail_fast:
                    return valid, headers, index, row

        if self.transform and any([is_dupe, is_empty, is_defective]):
            row = None

        return valid, headers, index, row
