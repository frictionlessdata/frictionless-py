from typing import TypedDict
from ..standards import IResource, IReport


class IRecord(TypedDict):
    path: str
    # TODO: use tableName
    table_name: str
    updated: str
    resource: IResource
    report: IReport
