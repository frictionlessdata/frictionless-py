# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from simpleeval import simple_eval
from ...registry import check


# Module API

@check('custom-constraint', type='custom', context='body')
class CustomConstraint(object):

    # Public

    def __init__(self, constraint, **options):
        self.__constraint = constraint

    def check_row(self, errors, cells, row_number):

        # Prepare names
        names = {}
        for cell in cells:
            if set(cell).issuperset(['header', 'value']):
                try:
                    names[cell['header']] = float(cell['value'])
                except ValueError:
                    pass

        # Check constraint
        try:
            # This call sould be considered as a safe expression evaluation
            # https://github.com/danthedeckie/simpleeval
            assert simple_eval(self.__constraint, names=names)
        except Exception:
            message = 'Custom constraint "%s" fails for row %s'
            return errors.append({
                'code': 'custom-constraint',
                'message': message % (self.__constraint, row_number),
                'row-number': row_number,
                'column-number': None,
            })
