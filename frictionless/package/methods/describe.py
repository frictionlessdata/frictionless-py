from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Type, Any

if TYPE_CHECKING:
    from ..package import Package
    from ...dialect import Dialect

# Describe


@classmethod
def describe(
    cls: Type[Package],
    source: Any,
    *,
    hashing: Optional[str] = None,
    dialect: Optional[Dialect] = None,
    stats: bool = False,
    **options,
):
    """Describe the given source as a package

    Parameters:
        source (any): data source
        stats? (bool): if `True` infer resource's stats
        **options (dict): Package constructor options

    Returns:
        Package: data package

    """
    package = cls(source, **options)
    if hashing:
        for resource in package.resources:
            resource.hashing = hashing
    if dialect:
        for resource in package.resources:
            resource.dialect = dialect
    package.infer(stats=stats)
    return package
