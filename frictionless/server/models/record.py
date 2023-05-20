from pydantic import BaseModel
from ..interfaces import IDescriptor
from .stats import Stats


class Record(BaseModel):
    id: str
    type: str
    path: str
    stats: Stats
    resource: IDescriptor
