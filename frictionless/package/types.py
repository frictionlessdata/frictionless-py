from __future__ import annotations

from typing import List

from typing_extensions import Required, TypedDict

from ..resource import IResource


class IPackage(TypedDict, total=False):
    name: str
    type: str
    title: str
    description: str
    resources: Required[List[IResource]]
