from __future__ import annotations
from typing import List
from typing_extensions import TypedDict
from .resource import IResource


class IPackage(TypedDict, total=False):
    name: str
    title: str
    description: str
    resources: List[IResource]
