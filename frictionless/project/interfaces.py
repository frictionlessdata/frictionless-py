from __future__ import annotations
from typing import List, Dict, Any
from typing_extensions import NotRequired, TypedDict


IHeader = List[str]
IRow = Dict[str, Any]


class IFileItem(TypedDict):
    path: str
    type: str


class IFile(IFileItem):
    path: str
    type: str
    record: NotRequired[IRecord]


class IRecordItem(TypedDict):
    path: str
    type: str
    updated: str
    tableName: NotRequired[str]


class IRecord(IRecordItem):
    resource: dict
    report: dict
    # TODO: use after pydantic@2
    #  resource: IResource
    #  report: IReport


class ITable(TypedDict):
    # TODO: rename to schema after pydantic@2
    tableSchema: Dict
    header: List[str]
    rows: List[IRow]
    # TODO: use after pydantic@2
    #  schema: ISchema


class IQueryData(TypedDict):
    header: IHeader
    rows: List[IRow]
