from __future__ import annotations
from typing import List, Dict, Any
from typing_extensions import Required, TypedDict


IDescriptor = Dict[str, Any]
IData = Dict[str, Any]
IHeader = List[str]
IRow = Dict[str, Any]
IChart = Dict[str, Any]


class IFileItem(TypedDict, total=False):
    path: Required[str]
    type: str


class IFile(IFileItem, total=False):
    record: IRecord


class IRecordItem(TypedDict, total=False):
    path: Required[str]
    type: Required[str]
    updated: Required[str]
    tableName: str
    errorCount: int


class IRecord(IRecordItem):
    resource: Dict[str, Any]
    report: Dict[str, Any]
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


class IResourceItem(TypedDict, total=False):
    id: Required[str]
    path: Required[str]
    errorCount: int
