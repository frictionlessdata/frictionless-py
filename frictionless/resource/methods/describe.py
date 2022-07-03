from __future__ import annotations
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from ..resource import Resource


@classmethod
def describe(cls: Type[Resource], source=None, *, stats=False, **options):
    """Describe the given source as a resource

    Parameters:
        source (any): data source
        stats? (bool): if `True` infer resource's stats
        **options (dict): Resource constructor options

    Returns:
        Resource: data resource

    """
    resource = cls(source, **options)
    resource.infer(stats=stats)
    return resource
