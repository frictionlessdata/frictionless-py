from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Type, Any

if TYPE_CHECKING:
    from ..resource import Resource


@classmethod
def describe(
    cls: Type[Resource],
    source: Optional[Any] = None,
    *,
    stats: bool = False,
    **options,
):
    """Describe the given source as a resource

    Parameters:
        source (any): data source
        stats? (bool): if `True` infer resource's stats
        **options (dict): Resource constructor options

    Returns:
        Resource: data resource

    """

    # Create resource
    resource = cls.from_options(source, **options)

    # Infer resource
    resource.infer(stats=stats)

    return resource
