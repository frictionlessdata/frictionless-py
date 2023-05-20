from __future__ import annotations
from typing import List, Dict, Any
from typing_extensions import TypedDict


IDescriptor = Dict[str, Any]
IHeader = List[str]
IRow = Dict[str, Any]
IChart = Dict[str, Any]


class IView(TypedDict):
    query: str
