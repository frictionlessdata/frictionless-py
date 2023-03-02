from __future__ import annotations
from typing import List, Dict, Any
from typing_extensions import Required, TypedDict


IData = Dict[str, Any]
IHeader = List[str]
IRow = Dict[str, Any]


class IFileItem(TypedDict, total=False):
    path: Required[str]
    type: str
    errorCount: int


class IFile(IFileItem, total=False):
    record: IRecord


class IRecordItem(TypedDict, total=False):
    path: Required[str]
    type: str
    updated: Required[str]
    tableName: str
    errorCount: int


class IRecord(IRecordItem):
    resource: dict
    report: dict
    # TODO: use after pydantic@2
    #  resource: IResource
    #  report: IReport


class IFieldItem(TypedDict):
    name: str
    type: str
    tableName: str
    tablePath: str


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
