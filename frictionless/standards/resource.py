from __future__ import annotations
from typing import List, Any
from typing_extensions import Required, TypedDict
from .dialect import IDialect
from .schema import ISchema


class IResource(TypedDict, total=False):
    name: Required[str]
    type: Required[str]
    title: str
    description: str
    path: str
    data: Any
    scheme: str
    format: str
    compression: str
    extrapaths: List[str]
    innerpath: str
    encoding: str
    dialect: IDialect
    schema: ISchema
