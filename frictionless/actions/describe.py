from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from ..resource import Resource

if TYPE_CHECKING:
    from ..metadata import Metadata


def describe(
    source: Optional[Any] = None,
    *,
    name: Optional[str] = None,
    type: Optional[str] = None,
    stats: bool = False,
    **options: Any,
) -> Metadata:
    """Describe the data source

    Parameters:
        source: data source
        name: resoucrce name
        type: data type: "package", "resource", "dialect", or "schema"
        stats: if `True` infer resource's stats
        **options: Resource constructor options

    Returns:
        Metadata: described metadata e.g. a Table Schema
    """
    return Resource.describe(source, name=name, type=type, stats=stats, **options)
