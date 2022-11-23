from __future__ import annotations
from typing import TYPE_CHECKING
from ...platform import platform
from ...system import Mapper

if TYPE_CHECKING:
    from ...schema import Schema


class ExcelMapper(Mapper):
    """Excel mapper"""

    def write_schema(self, schema: Schema, *, path: str) -> None:
        descriptor = schema.to_descriptor()
        platform.tableschema_to_template.create_xlsx(descriptor, path)
