from pydantic import BaseModel
from ..interfaces import IDescriptor
from .stats import Stats


class Record(BaseModel):
    name: str
    type: str
    path: str
    stats: Stats
    resource: IDescriptor
