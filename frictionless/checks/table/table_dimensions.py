from __future__ import annotations
import attrs
from typing import Optional
from ...checklist import Check
from ... import errors


@attrs.define(kw_only=True)
class table_dimensions(Check):
    """Check for minimum and maximum table dimensions"""

    type = "table-dimensions"
    Errors = [errors.TableDimensionsError]

    # State

    num_rows: Optional[int] = None
    """NOTE: add docs"""

    min_rows: Optional[int] = None
    """NOTE: add docs"""

    max_rows: Optional[int] = None
    """NOTE: add docs"""

    num_fields: Optional[int] = None
    """NOTE: add docs"""

    min_fields: Optional[int] = None
    """NOTE: add docs"""

    max_fields: Optional[int] = None
    """NOTE: add docs"""

    # Validate

    def validate_start(self):
        number_fields = len(self.resource.schema.fields)

        # Check if there is a different number of fields as required
        if self.num_fields and number_fields != self.num_fields:
            yield errors.TableDimensionsError(
                note="number of fields is %s, the required is %s"
                % (number_fields, self.num_fields),
            )

        # Check if there is less field than the minimum
        if self.min_fields and number_fields < self.min_fields:
            yield errors.TableDimensionsError(
                note="number of fields is %s, the minimum is %s"
                % (number_fields, self.min_fields),
            )

        # Check if there is more field than the maximum
        if self.max_fields and number_fields > self.max_fields:
            yield errors.TableDimensionsError(
                note="number of fields is %s, the maximum is %s"
                % (number_fields, self.max_fields),
            )

    def validate_end(self):
        number_rows = self.resource.stats.rows or 0

        # Check if doesn't have the exact number of rows
        if self.num_rows and number_rows != self.num_rows:
            yield errors.TableDimensionsError(
                note="number of rows is %s, the required is %s"
                % (number_rows, self.num_rows),
            )

        # Check if has less rows than the required
        if self.min_rows and number_rows < self.min_rows:
            yield errors.TableDimensionsError(
                note="number of rows is %s, the minimum is %s"
                % (number_rows, self.min_rows),
            )

        # Check if more rows than the required
        if self.max_rows and number_rows > self.max_rows:
            yield errors.TableDimensionsError(
                note="number of rows is %s, the maximum is %s"
                % (number_rows, self.max_rows),
            )

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "numRows": {"type": "number"},
            "minRows": {"type": "number"},
            "maxRows": {"type": "number"},
            "numFields": {"type": "number"},
            "minFields": {"type": "number"},
            "maxFields": {"type": "number"},
        },
    }
