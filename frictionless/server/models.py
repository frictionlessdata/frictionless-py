from typing import Optional
from pydantic import BaseModel

# Field


class FieldItem(BaseModel):
    name: str
    type: str
    tableName: str
    tablePath: str


# File


# Resource


class ResourceItem(BaseModel):
    id: str
    path: str
    datatype: str
    errors: Optional[int] = None


# Stats


class Stats(BaseModel):
    errors: int
