from copy import deepcopy
from tabulate import tabulate
from typing import Optional, List
from importlib import import_module
from dataclasses import dataclass, field as datafield
from ..exception import FrictionlessException
from ..metadata import Metadata
from .field import Field
from .. import settings
from .. import helpers
from .. import errors


@dataclass
class Schema(Metadata):
    """Schema representation

    This class is one of the cornerstones of of Frictionless framework.
    It allow to work with Table Schema and its fields.

    ```python
    schema = Schema('schema.json')
    schema.add_fied(Field(name='name', type='string'))
    ```
    """

    def __post_init__(self):

        # Connect fields
        for field in self.fields:
            field.schema = self

    # State

    fields: List[Field] = datafield(default_factory=list)
    """TODO: add docs"""

    missing_values: List[str] = datafield(
        default_factory=settings.DEFAULT_MISSING_VALUES.copy
    )
    """TODO: add docs"""

    primary_key: List[str] = datafield(default_factory=list)
    """TODO: add docs"""

    foreign_keys: List[dict] = datafield(default_factory=list)
    """TODO: add docs"""

    # Props

    @property
    def field_names(self):
        """List of field names"""
        return [field.name for field in self.fields]

    # Describe

    @staticmethod
    def describe(source, **options):
        """Describe the given source as a schema

        Parameters:
            source (any): data source
            **options (dict): describe resource options

        Returns:
            Schema: table schema
        """
        Resource = import_module("frictionless").Resource
        resource = Resource.describe(source, **options)
        schema = resource.schema
        return schema

    # Validate

    def validate(self):
        timer = helpers.Timer()
        errors = self.metadata_errors
        Report = import_module("frictionless").Report
        return Report.from_validation(time=timer.time, errors=errors)

    # Fields

    def add_field(self, field: Field) -> None:
        """Add new field to the schema"""
        self.fields.append(field)
        field.schema = self

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
        prev_field = self.get_field(name)
        descriptor = prev_field.to_descriptor()
        descriptor.update({"type": type})
        next_field = Field.from_descriptor(descriptor)
        self.set_field(next_field)
        return prev_field

    def remove_field(self, name: str) -> Field:
        """Remove field by name"""
        field = self.get_field(name)
        self.fields.remove(field)
        return field

    def clear_fields(self) -> None:
        """Remove all the fields"""
        self.fields = []

    # Read

    def read_cells(self, cells):
        """Read a list of cells (normalize/cast)

        Parameters:
            cells (any[]): list of cells

        Returns:
            any[]: list of processed cells
        """
        results = []
        readers = self.create_cell_readers()
        for index, reader in enumerate(readers.values()):
            cell = cells[index] if len(cells) > index else None
            results.append(reader(cell))
        return list(map(list, zip(*results)))

    def create_cell_readers(self):
        return {field.name: field.create_cell_reader() for field in self.fields}

    # Write

    # TODO: support types?
    def write_cells(self, cells, *, types=[]):
        """Write a list of cells (normalize/uncast)

        Parameters:
            cells (any[]): list of cells

        Returns:
            any[]: list of processed cells
        """
        results = []
        writers = self.create_cell_writers()
        for index, writer in enumerate(writers.values()):
            cell = cells[index] if len(cells) > index else None
            results.append(writer(cell))
        return list(map(list, zip(*results)))

    def create_cell_writers(self):
        return {field.name: field.create_cell_reader() for field in self.fields}

    # Convert

    # TODO: handle edge cases like wrong descriptor's prop types
    @classmethod
    def from_descriptor(cls, descriptor, **options):
        descriptor = super().metadata_normalize(descriptor)

        # Primary Key (v1)
        primary_key = descriptor.get("primaryKey")
        if primary_key and not isinstance(primary_key, list):
            descriptor["primaryKey"] = [primary_key]

        # Foreign Keys (v1)
        foreign_keys = descriptor.get("foreignKeys")
        if foreign_keys:
            for fk in foreign_keys:
                if not isinstance(fk, dict):
                    continue
                fk.setdefault("fields", [])
                fk.setdefault("reference", {})
                fk["reference"].setdefault("resource", "")
                fk["reference"].setdefault("fields", [])
                if not isinstance(fk["fields"], list):
                    fk["fields"] = [fk["fields"]]
                if not isinstance(fk["reference"]["fields"], list):
                    fk["reference"]["fields"] = [fk["reference"]["fields"]]

        return super().from_descriptor(descriptor, **options)

    @classmethod
    def from_jsonschema(cls, profile):
        """Create a Schema from JSONSchema profile

        Parameters:
            profile (str|dict): path or dict with JSONSchema profile

        Returns:
            Schema: schema instance
        """
        schema = Schema()
        profile = cls.metadata_normalize(profile)
        required = profile.get("required", [])
        assert isinstance(required, list)
        properties = profile.get("properties", {})
        assert isinstance(properties, dict)
        for name, prop in properties.items():

            # Type
            type = prop.get("type", "any")
            assert isinstance(type, str)
            if type not in ["string", "integer", "number", "boolean", "object", "array"]:
                type = "any"

            # Field
            assert isinstance(name, str)
            assert isinstance(prop, dict)
            field = Field.from_descriptor({"type": type})
            field.name = name
            schema.add_field(field)

            # Description
            description = prop.get("description")
            if description:
                assert isinstance(description, str)
                field.description = description

            # Required
            if name in required:
                field.required = True

        return schema

    def to_excel_template(self, path: str):
        """Export schema as an excel template

        Parameters:
            path: path of excel file to create with ".xlsx" extension

        Returns:
            any: excel template
        """
        backend = helpers.import_from_extras("tableschema_to_template", name="excel")
        return backend.create_xlsx(self.to_descriptor(), path)

    def to_summary(self) -> str:
        """Summary of the schema in table format"""
        content = [
            [field.name, field.type, True if field.required else ""]
            for field in self.fields
        ]
        return tabulate(content, headers=["name", "type", "required"], tablefmt="grid")

    # Metadata

    metadata_Error = errors.SchemaError  # type: ignore
    metadata_profile = deepcopy(settings.SCHEMA_PROFILE)
    metadata_profile["properties"]["fields"] = {"type": "array"}

    @classmethod
    def metadata_properties(cls):
        return super().metadata_properties(fields=Field)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Fields
        for field in self.fields:
            if field.builtin:
                yield from field.metadata_errors

        # Examples
        for field in [field for field in self.fields if field.example]:
            _, notes = field.read_cell(field.example)
            if notes is not None:
                note = 'example value for field "%s" is not valid' % field.name
                yield errors.SchemaError(note=note)

        # Primary Key
        for name in self.primary_key:
            if name not in self.field_names:
                note = 'primary key "%s" does not match the fields "%s"'
                note = note % (self.primary_key, self.field_names)
                yield errors.SchemaError(note=note)

        # Foreign Keys
        for fk in self.foreign_keys:
            for name in fk["fields"]:
                if name not in self.field_names:
                    note = 'foreign key "%s" does not match the fields "%s"'
                    note = note % (fk, self.field_names)
                    yield errors.SchemaError(note=note)
            if len(fk["fields"]) != len(fk["reference"]["fields"]):
                note = 'foreign key fields "%s" does not match the reference fields "%s"'
                note = note % (fk["fields"], fk["reference"]["fields"])
                yield errors.SchemaError(note=note)
