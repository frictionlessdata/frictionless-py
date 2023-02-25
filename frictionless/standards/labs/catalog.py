from __future__ import annotations
from typing import List, Union
from typing_extensions import TypedDict, Required
from ..core import IPackage


class ICatalog(TypedDict, total=False):
    name: str
    type: str
    title: str
    description: str
    datasets: Required[List[IDataset]]


class IDataset(TypedDict, total=False):
    name: Required[str]
    package: Required[Union[IPackage, str]]
