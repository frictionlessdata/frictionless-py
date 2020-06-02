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
        errors.BlankHeaderError,
        errors.DuplicateHeaderError,
        errors.ExtraHeaderError,
        errors.MissingHeaderError,
        errors.NonMatchingHeaderError,
        # body
        errors.BlankRowError,
        errors.ExtraCellError,
        errors.MissingCellError,
        errors.RequiredError,
        errors.TypeError,
        errors.ConstraintError,
    ]

    def validate_headers(self, headers):
        return headers.errors

    def validate_row(self, row):
        return row.errors
