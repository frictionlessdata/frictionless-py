from typing import Literal, Any, Dict, List, Union
from pydantic import BaseModel


class Change(BaseModel):
    type: str


class DeleteRow(Change):
    type: Literal["delete-row"]
    rowNumber: int


class UpdateCell(Change):
    type: Literal["update-cell"]
    rowNumber: int
    fieldName: str
    value: Any


class UpdateResource(Change):
    type: Literal["update-resource"]
    resource: Dict[str, Any]


class History(BaseModel):
    changes: List[Union[DeleteRow, UpdateCell, UpdateResource]]
