from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional, Union

import attrs
from tabulate import tabulate

from .. import errors, settings, types
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..platform import platform
from .factory import Factory
from .field import Field
from .types import INotes


@attrs.define(kw_only=True, repr=False)
class Schema(Metadata, metaclass=Factory):
    """Schema representation

    This class is one of the cornerstones of of Frictionless framework.
    It allow to work with Table Schema and its fields.

    ```python
    schema = Schema('schema.json')
    schema.add_fied(Field(name='name', type='string'))
    ```
    """

    descriptor: Optional[Union[types.IDescriptor, str]] = attrs.field(
        default=None, kw_only=False
    )
    """
    # TODO: add docs
    """

    # TODO: why it's optional??
    name: Optional[str] = None
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters.
    """

    type: ClassVar[Union[str, None]] = None
    """
    Type of the object
    """

    title: Optional[str] = None
    """
    A human-oriented title for the Schema.
    """

    description: Optional[str] = None
    """
    A brief description of the Schema.
    """

    fields: List[Field] = attrs.field(factory=list)
    """
    A List of fields in the schema.
    """

    missing_values: List[str] = attrs.field(factory=settings.DEFAULT_MISSING_VALUES.copy)
    """
    List of string values to be set as missing values in the schema fields. If any of string in
    missing values is found in any of the field value then it is set as None.
    """

    primary_key: List[str] = attrs.field(factory=list)
    """
    Specifies primary key for the schema.
    """

    foreign_keys: List[Dict[str, Any]] = attrs.field(factory=list)
    """
    Specifies the foreign keys for the schema.
    """

    def __attrs_post_init__(self):
        for field in self.fields:
            field.schema = self
        super().__attrs_post_init__()

    def __bool__(self):
        return bool(self.fields) or bool(self.to_descriptor())

    # Fields

    @property
    def field_names(self) -> List[str]:
        """List of field names"""
        # TODO: fix file.name is optional
        return [field.name for field in self.fields if field.name is not None]  # type: ignore

    @property
    def field_types(self) -> List[str]:
        """List of field types"""
        return [field.type for field in self.fields]

    def add_field(self, field: Field, *, position: Optional[int] = None) -> None:
        """Add new field to the schema"""
        field.schema = self
        if position is None:
            self.fields.append(field)
        else:
            self.fields.insert(position - 1, field)

    def has_field(self, name: str) -> bool:
        """Check if a field is present"""
        for field in self.fields:
            if field.name == name:
                return True
        return False

    def get_field(self, name: str) -> Field:
        """Get field by name"""
        for field in self.fields:
            if field.name == name:
                return field
        error = errors.SchemaError(note=f'field "{name}" does not exist')
        raise FrictionlessException(error)

    def set_field(self, field: Field) -> Optional[Field]:
        """Set field by name"""
        assert field.name
        if self.has_field(field.name):
            prev_field = self.get_field(field.name)
            index = self.fields.index(prev_field)
            self.fields[index] = field
            field.schema = self
            return prev_field
        self.add_field(field)

    def set_field_type(self, name: str, type: str) -> Field:
        """Set field type"""
        return self.update_field(name, {"type": type})

    def update_field(self, name: str, descriptor: types.IDescriptor) -> Field:
        """Update field"""
        prev_field = self.get_field(name)
        field_index = self.fields.index(prev_field)
        field_descriptor = prev_field.to_descriptor()
        field_descriptor.update(descriptor)
        new_field = Field.from_descriptor(field_descriptor)
        new_field.schema = self
        self.fields[field_index] = new_field
        return prev_field

    def remove_field(self, name: str) -> Field:
        """Remove field by name"""
        field = self.get_field(name)
        self.fields.remove(field)
        return field

    def clear_fields(self) -> None:
        """Remove all the fields"""
        self.fields = []

    def deduplicate_fields(self):
        if len(self.field_names) != len(set(self.field_names)):
            seen_names: List[str] = []
            for index, name in enumerate(self.field_names):
                count = seen_names.count(name) + 1
                if count > 1:
                    self.fields[index].name = "%s%s" % (name, count)
                seen_names.append(name)

    # Describe

    @staticmethod
    def describe(source: Optional[Any] = None, **options: Any) -> Schema:
        """Describe the given source as a schema

        Parameters:
            source (any): data source
            **options (dict): describe resource options

        Returns:
            Schema: table schema
        """
        Resource = platform.frictionless.Resource
        metadata = Resource.describe(source, type="schema", **options)
        assert isinstance(metadata, Schema)
        return metadata

    # Read

    def read_cells(self, cells: List[Any]):
        """Read a list of cells (normalize/cast)

        Parameters:
            cells (any[]): list of cells

        Returns:
            any[]: list of processed cells
        """
        res_cells: List[Any] = []
        res_notes: List[INotes] = []
        readers = self.create_cell_readers()
        for index, reader in enumerate(readers.values()):
            cell = cells[index] if len(cells) > index else None
            cell, notes = reader(cell)
            res_cells.append(cell)
            res_notes.append(notes)
        return res_cells, res_notes

    def create_cell_readers(self):
        return {field.name: field.create_cell_reader() for field in self.fields}

    # Write

    # TODO: support types?
    def write_cells(self, cells: List[Any], *, types: List[str] = []):
        """Write a list of cells (normalize/uncast)

        Parameters:
            cells (any[]): list of cells

        Returns:
            any[]: list of processed cells
        """
        res_cells: List[Any] = []
        res_notes: List[INotes] = []
        writers = self.create_cell_writers()
        for index, writer in enumerate(writers.values()):
            cell = cells[index] if len(cells) > index else None
            cell, notes = writer(cell)
            res_cells.append(cell)
            res_notes.append(notes)
        return res_cells, res_notes

    def create_cell_writers(self):
        return {field.name: field.create_cell_reader() for field in self.fields}

    # Flatten

    def flatten(self, spec: List[str] = ["name", "type"]):
        """Flatten the schema

        Parameters
            spec (str[]): flatten specification

        Returns:
            any[]: flatten schema
        """
        result: List[Any] = []
        for field in self.fields:
            context: Dict[str, Any] = {}
            context.update(field.to_descriptor())
            result.append([context.get(prop) for prop in spec])
        return result

    # Convert

    @classmethod
    def from_jsonschema(cls, profile: Union[types.IDescriptor, str]) -> Schema:
        """Create a Schema from JSONSchema profile

        Parameters:
            profile: path or dict with JSONSchema profile
        """
        profile = cls.metadata_retrieve(profile)
        mapper = platform.frictionless_formats.jsonschema.JsonschemaMapper()
        return mapper.read_schema(profile)

    def to_excel_template(self, path: str) -> None:
        """Export schema as an excel template

        Parameters:
            path: path of excel file to create with ".xlsx" extension
        """
        mapper = platform.frictionless_formats.excel.ExcelMapper()
        return mapper.write_schema(self, path=path)

    def to_summary(self) -> str:
        """Summary of the schema in table format"""
        content = [[f.name, f.type, True if f.required else ""] for f in self.fields]
        return tabulate(content, headers=["name", "type", "required"], tablefmt="grid")

    # Metadata

    metadata_type = "schema"
    metadata_Error = errors.SchemaError
    metadata_profile = {
        "type": "object",
        "required": ["fields"],
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "fields": {"type": "array"},
            "missingValues": {
                "type": "array",
                "items": {"type": "string"},
            },
            "primaryKey": {
                "type": "array",
                "items": {"type": "string"},
            },
            "foreignKeys": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "fields": {"type": "array", "items": {"type": "string"}},
                        "reference": {
                            "type": "object",
                            "required": ["resource", "fields"],
                            "properties": {
                                "resource": {"type": "string"},
                                "fields": {"type": "array", "items": {"type": "string"}},
                            },
                        },
                    },
                },
            },
        },
    }

    @classmethod
    def metadata_select_property_class(cls, name: str):
        if name == "fields":
            return Field

    # TODO: handle invalid structure
    @classmethod
    def metadata_transform(cls, descriptor: types.IDescriptor):
        super().metadata_transform(descriptor)

        # Primary Key (standards/v1)
        primary_key = descriptor.get("primaryKey")
        if primary_key and not isinstance(primary_key, list):
            descriptor["primaryKey"] = [primary_key]

        # Foreign Keys (standards/v1)
        foreign_keys = descriptor.get("foreignKeys")
        if foreign_keys:
            for fk in foreign_keys:
                if not isinstance(fk, dict):
                    continue
                fk.setdefault("fields", [])  # type: ignore
                fk.setdefault("reference", {})  # type: ignore
                fk["reference"].setdefault("resource", "")  # type: ignore
                fk["reference"].setdefault("fields", [])  # type: ignore
                if not isinstance(fk["fields"], list):
                    fk["fields"] = [fk["fields"]]
                if not isinstance(fk["reference"]["fields"], list):
                    fk["reference"]["fields"] = [fk["reference"]["fields"]]

    @classmethod
    def metadata_validate(cls, descriptor: types.IDescriptor):  # type: ignore
        metadata_errors = list(super().metadata_validate(descriptor))
        if metadata_errors:
            yield from metadata_errors
            return

        # Field Names
        field_names: List[str] = []
        for field in descriptor["fields"]:
            if "name" in field:
                field_names.append(field["name"])
        if len(field_names) != len(set(field_names)):
            note = "names of the fields are not unique"
            yield errors.SchemaError(note=note)

        # Primary Key
        pk = descriptor.get("primaryKey", [])
        for name in pk:
            if name not in field_names:
                note = 'primary key "%s" does not match the fields "%s"'
                note = note % (pk, field_names)
                yield errors.SchemaError(note=note)

        # Foreign Keys
        fks = descriptor.get("foreignKeys", [])
        for fk in fks:
            for name in fk["fields"]:
                if name not in field_names:
                    note = 'foreign key "%s" does not match the fields "%s"'
                    note = note % (fk, field_names)
                    yield errors.SchemaError(note=note)
            if len(fk["fields"]) != len(fk["reference"]["fields"]):
                note = 'foreign key fields "%s" does not match the reference fields "%s"'
                note = note % (fk["fields"], fk["reference"]["fields"])
                yield errors.SchemaError(note=note)
