from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Type, Any
from pathlib import Path
from ... import helpers

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

    # Support one fle path
    if not helpers.is_expandable_source(source):
        if isinstance(source, (str, Path)):
            source = [source]

    # Create package
    package = cls.from_options(source, **options)
    package.infer(stats=stats)
    return package
