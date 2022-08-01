from __future__ import annotations
import attrs
from typing import Optional, Any
from ...pipeline import Step


@attrs.define(kw_only=True)
class cell_convert(Step):
    """Convert cell

    Converts cell values of one or more fields using arbitrary functions, method
    invocations or dictionary translations.

    Parameters
    ----------
        type  : step identifier
        value : value to replace in cells.
        function : arbitrary function, data method or dictionary translations.
        field_name : field name to apply function to.

    Methods
    -------
        transform_resource(resource):
            converts cell value of a resource using arbitrary function, data method
            or dictionary translations

    Examples
    --------
    >>> from frictionless import Resource, Pipeline, steps
    >>> source = Resource(path="data/transform.csv")
        +----+-----------+------------+
        | id | name      | population |
        +====+===========+============+
        |  1 | 'germany' |         83 |
        +----+-----------+------------+
        |  2 | 'france'  |         66 |
        +----+-----------+------------+
        |  3 | 'spain'   |         47 |
        +----+-----------+------------+
    >>> # replacing value
    >>> pipeline = Pipeline(
            steps=[
                steps.cell_convert(field_name='population', value="100"),
            ],
        )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +----+-----------+------------+
        | id | name      | population |
        +====+===========+============+
        |  1 | 'germany' |        100 |
        +----+-----------+------------+
        |  2 | 'france'  |        100 |
        +----+-----------+------------+
        |  3 | 'spain'   |        100 |
        +----+-----------+------------+

    >>> # using lamda function
    >>> pipeline = Pipeline(
            steps=[
                steps.cell_convert(function=lambda v: v*2, field_name='population'),
            ],
        )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +----+-----------+------------+
        | id | name      | population |
        +====+===========+============+
        |  1 | 'germany' |     100100 |
        +----+-----------+------------+
        |  2 | 'france'  |     100100 |
        +----+-----------+------------+
        |  3 | 'spain'   |     100100 |
        +----+-----------+------------+

    >>> # using method of data value
    >>> pipeline = Pipeline(
            steps=[
                steps.cell_convert(function='upper', field_name='name'),
            ],
        )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +----+-----------+------------+
        | id | name      | population |
        +====+===========+============+
        |  1 | 'GERMANY' |     100100 |
        +----+-----------+------------+
        |  2 | 'FRANCE'  |     100100 |
        +----+-----------+------------+
        |  3 | 'SPAIN'   |     100100 |
        +----+-----------+------------+

    >>> # using a dictionary
    >>> pipeline = Pipeline(
            steps=[
                steps.cell_convert(field_name='name', function = {'GERMANY': 'Z', 'B': 'Y'}),
            ],
        )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +----+----------+------------+-----------------+
        | id | name     | population | avg_age         |
        +====+==========+============+=================+
        |  1 | 'Z'      |     100100 | Decimal('30.5') |
        +----+----------+------------+-----------------+
        |  2 | 'FRANCE' |     100100 | Decimal('30.0') |
        +----+----------+------------+-----------------+
        |  3 | 'SPAIN'  |     100100 | Decimal('40.0') |
        +----+----------+------------+-----------------+

    """

    type = "cell-convert"

    # State

    value: Optional[Any] = None
    """Value to replace in the field cell"""

    function: Optional[Any] = None
    """Function/Data method/Dictionary to apply to the column"""

    field_name: Optional[str] = None
    """Name of the field to apply the function"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        function = self.function
        if not self.field_name:
            if not function:
                function = lambda _: self.value
            resource.data = table.convertall(function)  # type: ignore
        elif self.function:
            resource.data = table.convert(self.field_name, function)  # type: ignore
        else:
            resource.data = table.update(self.field_name, self.value)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "value": {},
            "fieldName": {"type": "string"},
        },
    }
