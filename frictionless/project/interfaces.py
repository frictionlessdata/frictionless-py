from typing import List, Dict, Any
from typing_extensions import TypedDict


class IFileItem(TypedDict):
    path: str
    type: str


class IResourceListItem(TypedDict):
    path: str
    updated: str
    tableName: str


class IResourceItem(IResourceListItem):
    resource: dict
    report: dict
    # TODO: use after pydantic@2
    #  resource: IResource
    #  report: IReport


IQueryResult = List[Dict[str, Any]]
