import attrs
from typing import List
from ..schema import Schema
from .header import Header
from .row import Row


@attrs.define(kw_only=True, repr=False)
class Table:
    schema: Schema
    header: Header
    rows: List[Row]
