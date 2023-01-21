from __future__ import annotations
from typing import TypedDict, List
from typing_extensions import Required
from .checklist import IChecklist
from .pipeline import IPipeline
from .dialect import IDialect
from .schema import ISchema


class IResource(TypedDict, total=False):
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


class ITableResource(IResource, total=False):
    dialect: IDialect
    schema: Required[ISchema]
    checklist: IChecklist
    pipeline: IPipeline
