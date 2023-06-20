from typing import Any, List, Literal, Union

from pydantic import BaseModel


class Change(BaseModel):
    type: str


class RowDelete(Change):
    type: Literal["row-delete"]
    rowNumber: int


class CellUpdate(Change):
    type: Literal["cell-update"]
    rowNumber: int
    fieldName: str
    value: Any


class History(BaseModel):
    changes: List[Union[RowDelete, CellUpdate]]
