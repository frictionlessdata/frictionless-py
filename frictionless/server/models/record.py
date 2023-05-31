from pydantic import BaseModel
from .stats import Stats
from .. import types


class Record(BaseModel):
    name: str
    type: str
    path: str
    stats: Stats
    resource: types.IDescriptor
