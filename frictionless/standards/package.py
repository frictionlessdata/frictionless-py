from __future__ import annotations
from typing import List, Union
from typing_extensions import TypedDict, Required
from .resource import IResource


class IPackage(TypedDict, total=False):
    name: Required[str]
    type: Required[str]
    title: str
    description: str
    resources: Required[List[Union[IResource, str]]]
