from typing import Any, Optional
from ..dialect import Dialect
from ..resource import Resource
from ..package import Package
from ..schema import Schema
from ..system import system
from ..exception import FrictionlessException


def describe(
    source: Any = None,
    *,
    type: Optional[str] = None,
    expand: bool = False,
    stats: bool = False,
    **options,
):
    """Describe the data source

    API      | Usage
    -------- | --------
    Public   | `from frictionless import describe`

    Parameters:
        source (any): data source
        type (str): source type - `schema`, `resource` or `package` (default: infer)
        expand? (bool): if `True` it will expand the metadata
        stats? (bool): if `True` infer resource's stats
        **options (dict): options for the underlaying describe function

    Returns:
        Dialect|Package|Resource|Schema: metadata
    """

    # Infer type
    if not type:
        file = system.create_file(source, basepath=options.get("basepath", ""))
        type = "package" if file.multipart else "resource"

    # Describe dialect
    if type == "dialect":
        return Dialect.describe(source, expand=expand, **options)

    # Describe package
    elif type == "package":
        return Package.describe(source, expand=expand, stats=stats, **options)

    # Describe resource
    elif type == "resource":
        return Resource.describe(source, expand=expand, stats=stats, **options)

    # Describe schema
    elif type == "schema":
        return Schema.describe(source, expand=expand, **options)

    # Not supported
    raise FrictionlessException(f"Not supported describe type: {type}")
