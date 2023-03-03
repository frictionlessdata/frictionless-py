from __future__ import annotations
import builtins
from typing import TYPE_CHECKING, Optional

from frictionless.exception import FrictionlessException
from ..resource import Resource

if TYPE_CHECKING:
    from ..interfaces import IFilterFunction, IProcessFunction, IExtractedRows


class TableResource(Resource):
    type = "table"
    datatype = "table"

    # Extract

    def extract(
        self,
        *,
        name: Optional[str] = None,
        filter: Optional[IFilterFunction] = None,
        process: Optional[IProcessFunction] = None,
        limit_rows: Optional[int] = None,
    ) -> IExtractedRows:
        if not process:
            process = lambda row: row.to_dict()
        data = self.read_rows(size=limit_rows)
        data = builtins.filter(filter, data) if filter else data
        data = (process(row) for row in data) if process else data
        return {name or self.name: list(data)}
