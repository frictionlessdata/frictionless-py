from __future__ import annotations
from typing import List, Dict, Any
from typing_extensions import TypedDict


IDescriptor = Dict[str, Any]
IData = Dict[str, Any]
IHeader = List[str]
IRow = Dict[str, Any]
IChart = Dict[str, Any]


class ITable(TypedDict):
    # TODO: rename to schema after pydantic@2
    tableSchema: Dict[str, Any]
    header: List[str]
    rows: List[IRow]
    # TODO: use after pydantic@2
    #  schema: ISchema


class IQueryData(TypedDict):
    header: IHeader
    rows: List[IRow]


class IView(TypedDict):
    query: str
