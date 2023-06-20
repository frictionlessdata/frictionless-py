from __future__ import annotations

from typing import Any, Dict, List

from typing_extensions import TypedDict

IDescriptor = Dict[str, Any]
IHeader = List[str]
IRow = Dict[str, Any]
IChart = Dict[str, Any]


class IView(TypedDict):
    query: str
