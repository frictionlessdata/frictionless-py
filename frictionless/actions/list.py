from typing import Optional, List, Any
from ..resource import Resource


def list(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    **options,
) -> List[Resource]:
    """List resources

    Parameters:
        source: a data source
        type: data type
        **options: Resource options

    Returns:
        data resources
    """
    # List resources
    resource = Resource(source, datatype=type or "", **options)
    return resource.list()
