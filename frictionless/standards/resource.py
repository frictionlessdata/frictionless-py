from __future__ import annotations
from typing import List, Literal, Union
from typing_extensions import Required, TypedDict
from .dialect import IDialect
from .schema import ISchema


class IBaseResource(TypedDict, total=False):
    name: Required[str]
    title: str
    description: str
    path: Required[str]
    scheme: str
    format: str
    compression: str
    extrapaths: List[str]
    innerpath: str
    encoding: str
    dialect: IDialect


class IFileResource(IBaseResource, total=False):
    type: Required[Literal["file"]]


class ITableResource(IBaseResource, total=False):
    type: Required[Literal["table"]]
    schema: ISchema


IResource = Union[IFileResource, ITableResource]
