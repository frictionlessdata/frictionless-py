from __future__ import annotations
from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict


class IFileItem(TypedDict):
    path: str
    type: str


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
    rows: List[Dict[str, Any]]
    # TODO: use after pydantic@2
    #  schema: ISchema


IQueryResult = List[Dict[str, Any]]
