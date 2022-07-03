from __future__ import annotations
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from ..package import Package

# Describe


@classmethod
def describe(cls: Type[Package], source=None, *, stats=False, **options):
    """Describe the given source as a package

    Parameters:
        source (any): data source
        stats? (bool): if `True` infer resource's stats
        **options (dict): Package constructor options

    Returns:
        Package: data package

    """
    package = cls(source, **options)
    package.infer(stats=stats)
    return package
