from typing import TypedDict
from typing_extensions import Required


class IReportStats(TypedDict, total=False):
    tasks: Required[int]
    warnings: Required[int]
    errors: Required[int]
    seconds: Required[float]


class IReportTaskStats(TypedDict, total=False):
    md5: str
    sha256: str
    bytes: int
    fields: int
    rows: int
    warnings: Required[int]
    errors: Required[int]
    seconds: Required[float]
