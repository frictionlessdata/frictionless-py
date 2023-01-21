from typing import TypedDict
from ..standards import IResource, IReport


class IRecord(TypedDict):
    name: str
    path: str
    updated: str
    resource: IResource
    report: IReport
