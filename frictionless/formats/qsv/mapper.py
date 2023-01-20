from __future__ import annotations
from typing import List
from ...system import Mapper
from ...schema import Schema, Field


class QsvMapper(Mapper):

    # Read

    def read_schema(self, stats: List[dict]) -> Schema:
        """Convert "qsv stats" output to Table Schema"""
        schema = Schema()
        for item in stats:
            type = "string"
            if item["type"] == "Integer":
                type = "integer"
            elif item["type"] == "Float":
                type = "number"
            elif item["type"] == "DateTime":
                type = "datetime"
            elif item["type"] == "Date":
                type = "date"
            descriptor = {"name": item["field"], "type": type}
            schema.add_field(Field.from_descriptor(descriptor))
        return schema
