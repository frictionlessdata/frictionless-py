from pydantic import BaseModel

from .. import types


class Record(BaseModel):
    name: str
    type: str
    path: str
    resource: types.IDescriptor
