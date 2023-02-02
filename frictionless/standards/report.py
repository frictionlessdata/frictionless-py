from __future__ import annotations
from typing import List
from typing_extensions import Required, TypedDict


class IReport(TypedDict, total=False):
    name: str
    title: str
    description: str
    valid: Required[bool]
    warnings: List[str]
    errors: List
    tasks: List[IReportTask]


class IReportTask(TypedDict, total=False):
    valid: Required[bool]
    name: str
    type: str
    place: str
    warning: List
    errors: List
