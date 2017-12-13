# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from simpleeval import simple_eval
from ...registry import check
from ...error import Error


# Module API

@check('custom-constraint', type='custom', context='body')
class CustomConstraint(object):

    # Public

    def __init__(self, constraint, **options):
        self.__constraint = constraint

    def check_row(self, cells, row_number):
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
            message = 'Custom constraint "{constraint}" fails for row {row_number}'
            message_substitutions = {
                'constraint': self.__constraint,
            }
            error = Error(
                'custom-constraint',
                row_number=row_number,
                message=message,
                message_substitutions=message_substitutions
            )
            return [error]
