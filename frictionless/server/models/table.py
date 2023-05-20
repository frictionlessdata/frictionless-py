from typing import List
from pydantic import BaseModel
from ..interfaces import IDescriptor, IHeader, IRow


class Table(BaseModel):
    # TODO: rename to schema in pydantic@2
    tableSchema: IDescriptor
    header: IHeader
    rows: List[IRow]
