from typing import List
from copy import deepcopy
from tabulate import tabulate
from dataclasses import dataclass, field
from ..exception import FrictionlessException
from ..metadata2 import Metadata2
from ..field2 import Field2
from .describe import describe
from .validate import validate
from .. import settings
from .. import helpers
from .. import errors


@dataclass
class Schema2(Metadata2):
    """Schema representation

    This class is one of the cornerstones of of Frictionless framework.
    It allow to work with Table Schema and its fields.

    ```python
    schema = Schema('schema.json')
    schema.add_fied(Field(name='name', type='string'))
    ```
    """

    describe = staticmethod(describe)
    validate = validate

    # Properties

    fields: List[Field2] = field(default_factory=list)
    """TODO: add docs"""

    @property
    def field_names(self):
        """List of field names"""
        return [field.name for field in self.fields]

    missing_values: List[str] = field(
        default_factory=settings.DEFAULT_MISSING_VALUES.copy
    )
    """TODO: add docs"""

    primary_key: List[str] = field(default_factory=list)
    """TODO: add docs"""

    foreign_keys: List[dict] = field(default_factory=list)
    """TODO: add docs"""

    # Fields

    def has_field(self, name: str) -> bool:
        """Check if a field is present"""
        for field in self.fields:
            if field.name == name:
                return True
        return False

    def add_field(self, field: Field2) -> None:
        """Add new field to the schema"""
        self.fields.append(field)

    def get_field(self, name: str) -> Field2:
        """Get field by name"""
        for field in self.fields:
            if field.name == name:
                return field
        error = errors.SchemaError(note=f'field "{name}" does not exist')
        raise FrictionlessException(error)

    def remove_field(self, name: str) -> Field2:
        """Remove field by name"""
        field = self.get_field(name)
        self.fields.remove(field)
        return field

    # Read

    def read_cells(self, cells):
        """Read a list of cells (normalize/cast)

        Parameters:
            cells (any[]): list of cells

        Returns:
            any[]: list of processed cells
        """
        readers = self.create_cell_readers()
        return zip(*(reader(cells[idx]) for idx, reader in enumerate(readers.values())))

    def read_values(self, cells):
        readers = self.create_value_readers()
        return [reader(cells[index]) for index, reader in enumerate(readers.values())]

    def create_cell_readers(self):
        return {field.name: field.create_cell_reader() for field in self.fields}

    def create_value_readers(self):
        return {field.name: field.create_value_reader() for field in self.fields}

    # Write

    def write_cells(self, cells, *, types=[]):
        """Write a list of cells (normalize/uncast)

        Parameters:
            cells (any[]): list of cells

        Returns:
            any[]: list of processed cells
        """
        writers = self.create_cell_writers()
        return zip(*(writer(cells[idx]) for idx, writer in enumerate(writers.values())))

    def write_values(self, cells):
        writers = self.create_value_writers()
        return zip(writer(cells[index]) for index, writer in enumerate(writers.values()))

    def create_cell_writers(self):
        return {field.name: field.create_cell_reader() for field in self.fields}

    def create_value_writers(self):
        return {field.name: field.create_value_writer() for field in self.fields}

    # Convert

    @staticmethod
    def from_jsonschema(profile):
        """Create a Schema from JSONSchema profile

        Parameters:
            profile (str|dict): path or dict with JSONSchema profile

        Returns:
            Schema: schema instance
        """
        schema = Schema2()
        profile = Metadata2(profile).to_dict()
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
            field = Field2.from_descriptor({"type": type})
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
        tableschema_to_template = helpers.import_from_plugin(
            "tableschema_to_template", plugin="excel"
        )
        return tableschema_to_template.create_xlsx(self, path)

    # Summary

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
        return super().metadata_properties(fields=Field2)

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

    @classmethod
    def metadata_import(cls, descriptor):
        field = super().metadata_import(descriptor)

        # Normalize primary key
        if field.primary_key and not isinstance(field.primary_key, list):
            field.primary_key = [field.primary_key]

        # Normalize foreign keys
        if field.foreign_keys:
            for fk in field.foreign_keys:
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

        return field
