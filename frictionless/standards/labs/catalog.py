from __future__ import annotations
from typing import List, Union
from typing_extensions import TypedDict, Required
from .package import IPackage


class ICatalog(TypedDict, total=False):
    title: str
    description: str
    packages: Required[List[Union[IPackage, str]]]
