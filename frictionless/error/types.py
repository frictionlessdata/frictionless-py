from __future__ import annotations

from typing_extensions import Required, TypedDict


class IError(TypedDict, total=False):
    name: str
    type: Required[str]
    title: str
    description: str
