from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Type, Any

if TYPE_CHECKING:
    from ..package import Package

# Describe


@classmethod
def describe(
    cls: Type[Package],
    source: Optional[Any] = None,
    *,
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

    # Create package
    package = cls.from_options(source, **options)

    # Infer package
    package.infer(stats=stats)

    return package
