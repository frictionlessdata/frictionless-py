from typing import Optional
from pydantic import BaseModel


class Stats(BaseModel):
    errors: int


class ResourceItem(BaseModel):
    id: str
    path: str
    datatype: str
    errors: Optional[int] = None
