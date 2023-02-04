from __future__ import annotations
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict


IHeader = List[str]
IRow = List[Dict[str, Any]]


class IQueryData(TypedDict):
    header: IHeader
    rows: List[IRow]


# TODO: rename?
class IFileItem(TypedDict):
    path: str
    isFolder: bool


class IListedFile(TypedDict):
    path: str
    type: str
    updated: str
    tableName: Optional[str]


class IFile(IListedFile):
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


IQueryResult = List[Dict[str, Any]]
