from __future__ import annotations
from typing import List
from typing_extensions import TypedDict, Required
from ..resource import IResource


# TODO: replace by frictionless-standards
class IPackage(TypedDict, total=False):
    name: str
    type: str
    title: str
    description: str
    resources: Required[List[IResource]]
