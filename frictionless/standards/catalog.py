from __future__ import annotations
from typing import List
from typing_extensions import TypedDict, Required


class ICatalog(TypedDict, total=False):
    name: str
    type: str
    title: str
    description: str
    packages: Required[List[str]]
