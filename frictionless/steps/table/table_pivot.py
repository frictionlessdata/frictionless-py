from __future__ import annotations

import statistics
from typing import TYPE_CHECKING, Any, Callable

import attrs

from ... import errors
from ...exception import FrictionlessException
from ...pipeline import Step
from ...schema import Schema

if TYPE_CHECKING:
    from ...resource import Resource


# Mapping of petl aggregation function names to callables. This allows a
# string `aggfun` (e.g. coming from a JSON/YAML descriptor) to mirror the
# Python API, where a callable is passed directly.
AGGREGATION_FUNCTIONS: dict[str, Callable[[Any], Any]] = {
    "sum": sum,
    "max": max,
    "min": min,
    "len": len,
    "count": len,
    "mean": statistics.mean,
    "first": lambda values: list(values)[0],
    "last": lambda values: list(values)[-1],
}


@attrs.define(kw_only=True, repr=False)
class table_pivot(Step):
    """Pivot table.

    This step can be added using the `steps` parameter
    for the `transform` function.

    """

    type = "table-pivot"

    f1: str
    """
    Field that makes the rows in the output pivot table.
    """

    f2: str
    """
    Field that makes the columns in the output pivot table.
    """

    f3: str
    """
    Field that forms the data in the output pivot table.
    """

    aggfun: Any
    """
    Function to process and create data in the output pivot table.
    It can be a callable or, when defined via a descriptor, one of the
    supported aggregation function names: "sum", "max", "min", "len",
    "count", "mean", "first", "last".
    """

    # Transform

    def transform_resource(self, resource: Resource):
        table = resource.to_petl()  # type: ignore
        aggfun = self.aggfun
        if isinstance(aggfun, str):
            if aggfun not in AGGREGATION_FUNCTIONS:
                note = f'aggregation function "{aggfun}" is not supported'
                raise FrictionlessException(errors.StepError(note=note))
            aggfun = AGGREGATION_FUNCTIONS[aggfun]
        resource.data = table.pivot(self.f1, self.f2, self.f3, aggfun)  # type: ignore
        resource.schema = Schema()
        resource.infer()

    # Metadata

    metadata_profile_patch = {
        "required": ["f1", "f2", "f3", "aggfun"],
        "properties": {
            "f1": {"type": "string"},
            "f2": {"type": "string"},
            "f3": {"type": "string"},
            "aggfun": {},
        },
    }
