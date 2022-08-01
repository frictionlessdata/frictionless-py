from __future__ import annotations
import attrs
from typing import Optional
from ...platform import platform
from ...pipeline import Step


@attrs.define(kw_only=True)
class cell_replace(Step):
    """Replace cell

    Replace cell values in a given field or all fields using user defined pattern.

    Parameters
    ----------
        type : step identifier.
        pattern: pattern to search.
        replace: string to replace with.
        field_name : field name to apply the pattern.

    Methods
    -------
        transform_resource(resource):
            search cells with the given pattern in one or more fields and replace it with
            the user defined value.

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
    >>> # search all field cells for a given pattern and replace
    >>> pipeline = Pipeline(
        steps=[
            steps.cell_replace(pattern='denmark', replace="Denmark"),
        ],
    )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +-----------+--------------+--------------+
        | name      | country_code | city         |
        +===========+==============+==============+
        | 'germany' | 'DE'         | 'berlin'     |
        +-----------+--------------+--------------+
        | 'Denmark' | 'DK'         | 'copenhagen' |
        +-----------+--------------+--------------+
        | 'spain'   | 'ES'         | 'Andalusia'  |
        +-----------+--------------+--------------+

    >>> # search a specific field cells for a given pattern and replace
    >>> pipeline = Pipeline(
            steps=[
                steps.cell_replace(field_name="country_code", pattern='DE', replace="de"),
            ],
        )
    >>> target = source.transform(pipeline)
    >>> print(target.to_view())
        +-----------+--------------+--------------+
        | name      | country_code | city         |
        +===========+==============+==============+
        | 'germany' | 'de'         | 'berlin'     |
        +-----------+--------------+--------------+
        | 'Denmark' | 'DK'         | 'copenhagen' |
        +-----------+--------------+--------------+
        | 'spain'   | 'ES'         | 'Andalusia'  |
        +-----------+--------------+--------------+

    """

    type = "cell-replace"

    # State

    pattern: str
    """Pattern to search for in single or all fields"""

    replace: str
    """String to replace"""

    field_name: Optional[str] = None
    """field name to apply template string"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if not self.field_name:
            resource.data = table.replaceall(self.pattern, self.replace)  # type: ignore
        else:
            pattern = self.pattern
            function = platform.petl.replace
            if pattern.startswith("<regex>"):  # type: ignore
                pattern = pattern.replace("<regex>", "")  # type: ignore
                function = platform.petl.sub
            resource.data = function(table, self.field_name, pattern, self.replace)  # type: ignore

    # Metadata

    metadata_profile_patch = {
        "required": ["pattern"],
        "properties": {
            "pattern": {"type": "string"},
            "replace": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }
