from typing import Optional
from pydantic import BaseModel
from .interfaces import IDescriptor

# Column


class Column(BaseModel):
    name: str
    type: str
    tableName: str
    tablePath: str


# File


class File(BaseModel):
    type: str
    path: str
    errors: Optional[int] = None


# Record


class Record(BaseModel):
    id: str
    type: str
    path: str
    resource: IDescriptor


# Stats


class Stats(BaseModel):
    errors: int
