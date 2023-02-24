from __future__ import annotations
from typing import List
from typing_extensions import TypedDict, Required


class IPipeline(TypedDict, total=False):
    name: str
    title: str
    description: str
    steps: List[IStep]


class IStep(TypedDict, total=False):
    type: Required[str]
    title: str
    description: str
