from __future__ import annotations
from typing import TypedDict, List


class IPipeline(TypedDict, total=False):
    name: str
    title: str
    description: str
    steps: List[IStep]


class IStep(TypedDict, total=False):
    type: str
    title: str
    description: str
