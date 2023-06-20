from __future__ import annotations

from typing import TYPE_CHECKING

import attrs
import simpleeval  # type: ignore

from ... import errors
from ...checklist import Check

if TYPE_CHECKING:
    from ...table import Row


@attrs.define(kw_only=True, repr=False)
class row_constraint(Check):
    """Check that every row satisfies a provided Python expression."""

    type = "row-constraint"
    Errors = [errors.RowConstraintError]

    formula: str
    """
    Python expression to apply to all rows. To evaluate the forumula
    simpleeval library is used.
    """

    # Validate

    def validate_row(self, row: Row):
        try:
            # This call should be considered as a safe expression evaluation
            # https://github.com/danthedeckie/simpleeval
            # NOTE: review EvalWithCompoundTypes/sync with steps
            evalclass = simpleeval.EvalWithCompoundTypes  # type: ignore
            assert evalclass(names=row).eval(self.formula)  # type: ignore
        except Exception:
            yield errors.RowConstraintError.from_row(
                row,
                note='the row constraint to conform is "%s"' % self.formula,
            )

    # Metadata

    metadata_profile_patch = {
        "required": ["formula"],
        "properties": {
            "formula": {"type": "string"},
        },
    }
