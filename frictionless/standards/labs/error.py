from __future__ import annotations
from typing_extensions import TypedDict, Required


class IError(TypedDict, total=False):
    name: str
    type: Required[str]
    title: str
    description: str
