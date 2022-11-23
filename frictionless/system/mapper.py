from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..schema import Schema


# NOTE:
# Extend this interface while new mappers appear


class Mapper:

    # Read

    def read_schema(self, *args, **kwargs) -> Schema:
        raise NotImplementedError()

    # Write

    def write_schema(self, schema: Schema, **kwargs) -> Any:
        raise NotImplementedError()
