from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...interfaces import IFilterFunction, IProcessFunction
    from ..package import Package


def extract(
    self: Package,
    *,
    limit_rows: Optional[int] = None,
    process: Optional[IProcessFunction] = None,
    filter: Optional[IFilterFunction] = None,
    stream: bool = False,
):
    """Extract package rows

    Parameters:
        filter? (bool): a row filter function
        process? (func): a row processor function
        stream? (bool): return a row streams instead of loading into memory

    Returns:
        {path: Row[]}: a dictionary of arrays/streams of rows

    """

    # Prepare package
    self.infer(sample=False)

    # Extract tables
    tables = {}
    for resource in self.resources:
        tables[resource.name] = resource.extract(
            limit_rows=limit_rows,
            process=process,
            filter=filter,
            stream=stream,
        )

    return tables
