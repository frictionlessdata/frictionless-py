from __future__ import annotations
from typing import List
from typing_extensions import TypedDict


class IChecklist(TypedDict, total=False):
    name: str
    title: str
    description: str
    checks: List[ICheck]
    pickErrors: List[str]
    skipErrors: List[str]


class ICheck(TypedDict, total=False):
    type: str
    title: str
    description: str
