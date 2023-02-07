from __future__ import annotations
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict


IHeader = List[str]
IRow = Dict[str, Any]


# NOTE: later can be extended to have whatever the filemanager needs
class IFileItem(TypedDict):
    path: str
    type: str


class IFileRecord(IFileItem):
    updated: str
    tableName: Optional[str]


class IFile(IFileRecord):
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
