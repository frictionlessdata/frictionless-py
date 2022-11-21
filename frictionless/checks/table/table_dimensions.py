from __future__ import annotations
import attrs
from typing import Optional
from ...checklist import Check
from ... import errors


@attrs.define(kw_only=True)
class table_dimensions(Check):
    """Check for minimum and maximum table dimensions."""

    type = "table-dimensions"
    Errors = [errors.TableDimensionsError]

    # State

    num_rows: Optional[int] = None
    """
    Specify the number of rows to compare with actual rows in
    the table. If the actual number of rows are less than num_rows it will 
    notify user as errors.
    """

    min_rows: Optional[int] = None
    """
    Specify the minimum number of rows that should be in the table. 
    If the actual number of rows are less than min_rows it will notify user 
    as errors.
    """

    max_rows: Optional[int] = None
    """
    Specify the maximum number of rows allowed. 
    If the actual number of rows are more than max_rows it will notify user 
    as errors.
    """

    num_fields: Optional[int] = None
    """
    Specify the number of fields to compare with actual fields in
    the table. If the actual number of fields are less than num_fields it will 
    notify user as errors.
    """

    min_fields: Optional[int] = None
    """
    Specify the minimum number of fields that should be in the table. 
    If the actual number of fields are less than min_fields it will notify user 
    as errors.
    """

    max_fields: Optional[int] = None
    """
    Specify the maximum number of expected fields. 
    If the actual number of fields are more than max_fields it will notify user 
    as errors.
    """

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
