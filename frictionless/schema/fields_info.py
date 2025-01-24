from typing import List

from frictionless.schema.field import Field


class FieldInfo:
    """Private class to store additional data to a field"""

    def __init__(self, field: Field, field_number: int):
        """field_number: 1-indexed rank of the field"""
        self.field = field
        self.field_number = field_number
        self.cell_reader = field.create_cell_reader()
        self.cell_writer = field.create_cell_writer()


class FieldsInfo:
    def __init__(self, fields: List[Field]):
        self._fields: List[FieldInfo] = [
            FieldInfo(field, i + 1) for i, field in enumerate(fields)
        ]

    def ls(self) -> List[str]:
        """List all field names"""
        return [fi.field.name for fi in self._fields]

    def get(self, field_name: str) -> FieldInfo:
        """Get a Field by its name

        Raises:
            ValueError: Field with name fieldname does not exist
        """
        try:
            return next(fi for fi in self._fields if fi.field.name == field_name)
        except StopIteration:
            raise ValueError(f"'{field_name}' is not in fields data")

    def get_copies(self) -> List[Field]:
        """Return field copies"""
        return [fi.field.to_copy() for fi in self._fields]

    def rm(self, field_name: str):
        try:
            i = self.ls().index(field_name)
            del self._fields[i]
        except ValueError:
            raise ValueError(f"'{field_name}' is not in fields data")
