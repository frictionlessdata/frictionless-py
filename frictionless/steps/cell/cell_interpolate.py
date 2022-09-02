from __future__ import annotations
import attrs
from typing import Optional
from ...pipeline import Step


@attrs.define(kw_only=True)
class cell_interpolate(Step):
    """Interpolate cell

    Interpolate all values in a given or all string fields using the `template` string.

    Parameters
    ----------
        type : step identifier.
        template: template string to apply to the string fields.
        field_name : field name to apply the format.

    Methods
    -------
        transform_resource(resource):
            interpolate cells of given or all string fields using user defined template.

    Examples
    --------
    >>> from frictionless import Resource, Pipeline, steps
    >>> source = Resource(path="data/transform-string.csv")
    >>> print(source.to_view())
        +-----------+--------------+--------------+
        | name      | country_code | city         |
        +===========+==============+==============+
        | 'germany' | 'DE'         | 'berlin'     |
        +-----------+--------------+--------------+
        | 'denmark' | 'DK'         | 'copenhagen' |
        +-----------+--------------+--------------+
        | 'spain'   | 'ES'         | 'Andalusia'  |
        +-----------+--------------+--------------+
    >>> # apply template string to a specific field
    >>> pipeline = Pipeline(
            steps=[
                steps.cell_interpolate(field_name='name', template="Prefix: %s"),
            ],
        )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +-------------------+--------------+--------------+
        | name              | country_code | city         |
        +===================+==============+==============+
        | 'Prefix: germany' | 'DE'         | 'berlin'     |
        +-------------------+--------------+--------------+
        | 'Prefix: denmark' | 'DK'         | 'copenhagen' |
        +-------------------+--------------+--------------+
        | 'Prefix: spain'   | 'ES'         | 'Andalusia'  |
        +-------------------+--------------+--------------+

    >>> # apply template string to all fields
    >>> pipeline = Pipeline(
            steps=[
                steps.cell_interpolate(template="Prefix: %s"),
            ],
        )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +-------------------+--------------+----------------------+
        | name              | country_code | city                 |
        +===================+==============+======================+
        | 'Prefix: germany' | 'Prefix: DE' | 'Prefix: berlin'     |
        +-------------------+--------------+----------------------+
        | 'Prefix: denmark' | 'Prefix: DK' | 'Prefix: copenhagen' |
        +-------------------+--------------+----------------------+
        | 'Prefix: spain'   | 'Prefix: ES' | 'Prefix: Andalusia'  |
        +-------------------+--------------+----------------------+

    """

    type = "cell-interpolate"

    # State

    template: str
    """template string to apply to the field cells"""

    field_name: Optional[str] = None
    """field name to apply template string"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if not self.field_name:
            resource.data = table.interpolateall(self.template)  # type: ignore
        else:
            resource.data = table.interpolate(self.field_name, self.template)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["template"],
        "properties": {
            "template": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }
