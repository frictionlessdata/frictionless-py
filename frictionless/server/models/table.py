from typing import List

from pydantic import BaseModel

from .. import types


class Table(BaseModel):
    # TODO: rename to schema in pydantic@2
    tableSchema: types.IDescriptor
    header: types.IHeader
    rows: List[types.IRow]
