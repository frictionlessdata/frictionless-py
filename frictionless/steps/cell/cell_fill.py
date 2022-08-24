from __future__ import annotations
import attrs
from typing import Optional, Any
from ...pipeline import Step


@attrs.define(kw_only=True)
class cell_fill(Step):
    """Fill cell

    Replaces missing values with non-missing values from the adjacent row/column.

    Parameters
    ----------
        type : step identifier
        value : value to replace in cells.
        field_name : field name to apply function to.
        direction: column/row direction from where to copy the non-missing value.
                   for column cells, it also checks for the field types and only works
                   if the two columns are of same types.


    Methods
    -------
        transform_resource(resource):
            replaces cell value of a resource using adjacent row/column value or using
            user defined value.

    Examples
    --------
    >>> from frictionless import Resource, Pipeline, steps
    >>> source = Resource(path="data/transform-missing.csv")
        +----+-----------+-----------+-----------------+-----------------+
        | id | name      | title     | population      | avg_age         |
        +====+===========+===========+=================+=================+
        |  1 | 'germany' | 'germany' | Decimal('30.5') | None            |
        +----+-----------+-----------+-----------------+-----------------+
        |  2 | None      | 'italy'   |   Decimal('66') | Decimal('35.0') |
        +----+-----------+-----------+-----------------+-----------------+
        |  3 | 'spain'   | 'spain'   | Decimal('50.0') | None            |
        +----+-----------+-----------+-----------------+-----------------+
    >>> # replacing missing values by user defined value
    >>> pipeline = Pipeline(
            steps=[
                steps.table_normalize(),
                steps.cell_fill(field_name="name", value="france"),
            ],
        )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +----+-----------+-----------+-----------------+-----------------+
        | id | name      | title     | population      | avg_age         |
        +====+===========+===========+=================+=================+
        |  1 | 'germany' | 'germany' | Decimal('30.5') | None            |
        +----+-----------+-----------+-----------------+-----------------+
        |  2 | 'france'  | 'italy'   |   Decimal('66') | Decimal('35.0') |
        +----+-----------+-----------+-----------------+-----------------+
        |  3 | 'spain'   | 'spain'   | Decimal('50.0') | None            |
        +----+-----------+-----------+-----------------+-----------------+

    >>> # using non-missing value from the row above
    >>> pipeline = pipeline = Pipeline(
            steps=[
                steps.table_normalize(),
                steps.cell_fill(direction="down"),
            ],
        )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +----+-----------+-----------+-----------------+-----------------+
        | id | name      | title     | population      | avg_age         |
        +====+===========+===========+=================+=================+
        |  1 | 'germany' | 'germany' | Decimal('30.5') | None            |
        +----+-----------+-----------+-----------------+-----------------+
        |  2 | 'france'  | 'italy'   |   Decimal('66') | Decimal('35.0') |
        +----+-----------+-----------+-----------------+-----------------+
        |  3 | 'spain'   | 'spain'   | Decimal('50.0') | Decimal('35.0') |
        +----+-----------+-----------+-----------------+-----------------+

    >>> # using non-missing value from the right column
    >>> pipeline = Pipeline(
            steps=[
                steps.table_normalize(),
                steps.cell_fill(direction="left"),
            ],
        )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +----+-----------+-----------+-----------------+-----------------+
        | id | name      | title     | population      | avg_age         |
        +====+===========+===========+=================+=================+
        |  1 | 'germany' | 'germany' | Decimal('30.5') | None            |
        +----+-----------+-----------+-----------------+-----------------+
        |  2 | 'france'  | 'italy'   |   Decimal('66') | Decimal('35.0') |
        +----+-----------+-----------+-----------------+-----------------+
        |  3 | 'spain'   | 'spain'   | Decimal('50.0') | Decimal('35.0') |
        +----+-----------+-----------+-----------------+-----------------+

    >>> # using non-missing value from the left column
    >>> pipeline = Pipeline(
            steps=[
                steps.table_normalize(),
                steps.cell_fill(direction="right"),
            ],
        )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +----+-----------+-----------+-----------------+-----------------+
        | id | name      | title     | population      | avg_age         |
        +====+===========+===========+=================+=================+
        |  1 | 'germany' | 'germany' | Decimal('30.5') | Decimal('30.5') |
        +----+-----------+-----------+-----------------+-----------------+
        |  2 | 'france'  | 'italy'   |   Decimal('66') | Decimal('35.0') |
        +----+-----------+-----------+-----------------+-----------------+
        |  3 | 'spain'   | 'spain'   | Decimal('50.0') | Decimal('35.0') |
        +----+-----------+-----------+-----------------+-----------------+

    """

    type = "cell-fill"

    # State

    value: Optional[Any] = None
    """Value to replace in the field cell with missing value"""

    field_name: Optional[str] = None
    """Name of the field to replace the missing value cells"""

    direction: Optional[str] = None
    """Directions to read the non missing value from(left/right/above)"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if self.value:
            resource.data = table.convert(self.field_name, {None: self.value})  # type: ignore
        elif self.direction == "down":
            if self.field_name:
                resource.data = table.filldown(self.field_name)  # type: ignore
            else:
                resource.data = table.filldown()  # type: ignore
        elif self.direction == "right":
            resource.data = table.fillright()  # type: ignore
        elif self.direction == "left":
            resource.data = table.fillleft()  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "value": {},
            "fieldName": {"type": "string"},
            "direction": {
                "type": "string",
                "enum": ["down", "right", "left"],
            },
        },
    }
