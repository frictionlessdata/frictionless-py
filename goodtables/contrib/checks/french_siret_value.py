# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from simpleeval import simple_eval
import stdnum.fr.siret
from ...registry import check
from ...error import Error


# Module API

@check('french-siret-value', type='custom', context='body')
class FrenchSiretValue(object):

    # Public

    def __init__(self, column, **options):
        self.__column = column

    def check_row(self, cells):
        # Get cell
        cell = None
        for item in cells:
            if self.__column in [item['column-number'], item['header']]:
                cell = item
                break

        # Check cell
        if not cell:
            return

        # Check value
        value = cell.get('value')
        if not stdnum.fr.siret.is_valid(value):
            message = "La valeur \"{value}\" n'est pas un numéro SIRET français valide."
            message_substitutions = {
                'value': value,
            }
            error = Error(
                'french-siret-value',
                cell,
                message=message,
                message_substitutions=message_substitutions
            )
            return [error]
