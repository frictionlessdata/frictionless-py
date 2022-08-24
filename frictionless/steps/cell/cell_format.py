from __future__ import annotations
import attrs
from typing import Optional
from ...pipeline import Step


@attrs.define(kw_only=True)
class cell_format(Step):
    """Format cell

    Formats all values in the given or all string fields using the `template` format string.

    Parameters
    ----------
        type : step identifier
        template: template to apply format string.
        field_name : field name to apply the format.

    Methods
    -------
        transform_resource(resource):
            format cells of given or all string fields using user defined template.

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
    >>> # apply format to a specific field
    >>> pipeline = Pipeline(
            steps=[
                steps.cell_format(template="Prefix: {0}", field_name="name"),
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

    >>> # apply format to all fields
    >>> pipeline = Pipeline(
        steps=[
            steps.cell_format(template="Prefix: {0}"),
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

    type = "cell-format"

    # State

    template: str
    """format string to apply to cells"""

    field_name: Optional[str] = None
    """field name to apply template format"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if not self.field_name:
            resource.data = table.formatall(self.template)  # type: ignore
        else:
            resource.data = table.format(self.field_name, self.template)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["template"],
        "properties": {
            "template": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }
