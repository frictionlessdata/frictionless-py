from typing import Any, Optional
from ..dialect import Dialect
from ..resource import Resource
from ..package import Package
from ..schema import Schema
from ..exception import FrictionlessException
from .. import helpers


def describe(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    stats: bool = False,
    **options,
):
    """Describe the data source

    Parameters:
        source (any): data source
        type (str): source type - `schema`, `resource` or `package` (default: infer)
        stats? (bool): if `True` infer resource's stats
        **options (dict): options for the underlaying describe function

    Returns:
        Metadata: described metadata e.g. a Table Schema
    """

    # Detect type
    if not type:
        type = "resource"
        if helpers.is_expandable_source(source):
            type = "package"

    # Describe resource
    if type == "resource":
        return Resource.describe(source, stats=stats, **options)

    # Describe package
    if type == "package":
        return Package.describe(source, stats=stats, **options)

    # Describe dialect
    if type == "dialect":
        return Dialect.describe(source, **options)

    # Describe schema
    if type == "schema":
        return Schema.describe(source, **options)

    # Not supported
    raise FrictionlessException(f"Not supported describe type: {type}")
