from __future__ import annotations

from typing import List

from typing_extensions import Required, TypedDict


class IPipeline(TypedDict, total=False):
    name: str
    type: str
    title: str
    description: str
    steps: Required[List[IStep]]


class IStep(TypedDict, total=False):
    name: str
    type: Required[str]
    title: str
    description: str
