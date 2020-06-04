from ..check import Check
from .. import errors


class BaselineCheck(Check):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'properties': {},
        'additionalProperties': False,
    }
    possible_Errors = [  # type: ignore
        # head
        errors.ExtraHeaderError,
        errors.MissingHeaderError,
        errors.BlankHeaderError,
        errors.DuplicateHeaderError,
        errors.NonMatchingHeaderError,
        # body
        errors.ExtraCellError,
        errors.MissingCellError,
        errors.BlankRowError,
        errors.RequiredError,
        errors.TypeError,
        errors.ConstraintError,
    ]

    def validate_headers(self, headers):
        return headers.errors

    def validate_row(self, row):
        return row.errors
