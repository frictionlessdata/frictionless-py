from __future__ import annotations
from typing import List, Literal, Union
from typing_extensions import Required, TypedDict
from .checklist import IChecklist
from .pipeline import IPipeline
from .dialect import IDialect
from .schema import ISchema


class IBaseResource(TypedDict, total=False):
    name: Required[str]
    title: str
    description: str
    path: Required[str]
    scheme: Required[str]
    format: Required[str]
    encoding: Required[str]
    mediatype: Required[str]
    compression: str
    innerpath: List[str]
    extrapaths: List[str]


class IFileResource(IBaseResource, total=False):
    type: Required[Literal["file"]]


class ITableResource(IBaseResource, total=False):
    type: Required[Literal["table"]]
    dialect: IDialect
    schema: Required[ISchema]
    checklist: IChecklist
    pipeline: IPipeline


IResource = Union[IFileResource, ITableResource]
