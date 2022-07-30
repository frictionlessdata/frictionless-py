from __future__ import annotations
import re
import attrs
import decimal
from functools import partial
from importlib import import_module
from typing import TYPE_CHECKING, ClassVar, Optional, List
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..system import system
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from .schema import Schema


@attrs.define(kw_only=True)
class Field(Metadata):
    """Field representation"""

    type: ClassVar[str]
    """TODO: add docs"""

    builtin: ClassVar[bool] = False
    """TODO: add docs"""

    supported_constraints: ClassVar[List[str]] = []
    """TODO: add docs"""

    # State

    name: Optional[str] = None
    """TODO: add docs"""

    title: Optional[str] = None
    """TODO: add docs"""

    description: Optional[str] = None
    """TODO: add docs"""

    format: str = settings.DEFAULT_FIELD_FORMAT
    """TODO: add docs"""

    missing_values: List[str] = attrs.field(factory=settings.DEFAULT_MISSING_VALUES.copy)
    """TODO: add docs"""

    constraints: dict = attrs.field(factory=dict)
    """TODO: add docs"""

    rdf_type: Optional[str] = None
    """TODO: add docs"""

    example: Optional[str] = None
    """TODO: add docs"""

    schema: Optional[Schema] = None
    """TODO: add docs"""

    # Props

    @property
    def required(self):
        """TODO: add docs"""
        return self.constraints.get("required", False)

    @required.setter
    def required(self, value: bool):
        self.constraints["required"] = value

    # Read

    def read_cell(self, cell):
        cell_reader = self.create_cell_reader()
        return cell_reader(cell)

    def create_cell_reader(self):
        value_reader = self.create_value_reader()

        # Create missing values
        missing_values = self.missing_values
        if not self.has_defined("missing_values") and self.schema:
            missing_values = self.schema.missing_values

        # TODO: review where we need to cast constraints
        # Create checks
        checks = {}
        for name in self.supported_constraints:
            constraint = self.constraints.get(name)
            if constraint is not None:
                if name in ["minimum", "maximum"]:
                    constraint = value_reader(constraint)
                if name == "pattern":
                    constraint = re.compile("^{0}$".format(constraint))
                if name == "enum":
                    constraint = list(map(value_reader, constraint))  # type: ignore
                checks[name] = partial(globals().get(f"check_{name}"), constraint)  # type: ignore

        # Create reader
        def cell_reader(cell):
            notes = None
            if cell in missing_values:
                cell = None
            if cell is not None:
                cell = value_reader(cell)
                if cell is None:
                    notes = notes or {}
                    notes["type"] = f'type is "{self.type}/{self.format}"'
            if not notes and checks:
                for name, check in checks.items():
                    if not check(cell):
                        notes = notes or {}
                        constraint = self.constraints[name]
                        notes[name] = f'constraint "{name}" is "{constraint}"'
            return cell, notes

        return cell_reader

    def create_value_reader(self):

        # Create reader
        def value_reader(cell):
            return cell

        return value_reader

    # Write

    def write_cell(self, cell, *, ignore_missing=False):
        cell_writer = self.create_cell_writer()
        return cell_writer(cell, ignore_missing=ignore_missing)

    def create_cell_writer(self):
        value_writer = self.create_value_writer()

        # Create missing value
        try:
            missing_value = self.missing_values[0]
            if not self.has_defined("missing_values") and self.schema:
                missing_value = self.schema.missing_values[0]
        except IndexError:
            missing_value = settings.DEFAULT_MISSING_VALUES[0]

        # Create writer
        def cell_writer(cell, *, ignore_missing=False):
            notes = None
            if cell is None:
                cell = cell if ignore_missing else missing_value
                return cell, notes
            cell = value_writer(cell)
            if cell is None:
                notes = notes or {}
                notes["type"] = f'type is "{self.type}/{self.format}"'
            return cell, notes

        return cell_writer

    def create_value_writer(self):

        # Create writer
        def value_writer(cell):
            return str(cell)

        return value_writer

    # Metadata

    metadata_type = "field"
    metadata_Error = errors.FieldError
    metadata_profile = {
        "type": "object",
        "required": ["name", "type"],
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "format": {"type": "string"},
            "missingValues": {
                "type": "array",
                "items": {"type": "string"},
            },
            "constraints": {
                "type": "object",
                "properties": {
                    "required": {"type": "boolean"},
                    "unique": {"type": "boolean"},
                    "pattern": {"type": "string"},
                    "enum": {"type": "array"},
                    "minLength": {"type": "integer"},
                    "maxLength": {"type": "integer"},
                    "minimum": {},
                    "maximum": {},
                },
            },
            "rdfType": {"type": "string"},
            "example": {},
        },
    }

    @classmethod
    def metadata_import(cls, descriptor):
        descriptor = cls.metadata_normalize(descriptor)
        if cls is Field:
            try:
                return system.create_field(descriptor)
            except FrictionlessException:
                fields = import_module("frictionless").fields
                return fields.AnyField.from_descriptor(descriptor)

        # Format (v0)
        format = descriptor.get("format")
        if format and isinstance(format, str) and format.startswith("fmt:"):
            descriptor["format"] = format.replace("fmt:", "")

        return super().metadata_import(descriptor)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Constraints
        for name in self.constraints.keys():
            if name not in self.supported_constraints + ["unique"]:
                note = f'constraint "{name}" is not supported by type "{self.type}"'
                yield errors.FieldError(note=note)

        # Custom
        for name in ["required"]:
            if name in self.custom:
                note = f'"{name}" should be set as "constraints.{name}"'
                yield errors.FieldError(note=note)


# Internal


def check_required(constraint, cell):
    if not (constraint and cell is None):
        return True
    return False


def check_minLength(constraint, cell):
    if cell is None:
        return True
    if len(cell) >= constraint:
        return True
    return False


def check_maxLength(constraint, cell):
    if cell is None:
        return True
    if len(cell) <= constraint:
        return True
    return False


def check_minimum(constraint, cell):
    if cell is None:
        return True
    try:
        if cell >= constraint:
            return True
    except decimal.InvalidOperation:
        # For non-finite numbers NaN, INF and -INF
        # the constraint always is not satisfied
        return False
    return False


def check_maximum(constraint, cell):
    if cell is None:
        return True
    try:
        if cell <= constraint:
            return True
    except decimal.InvalidOperation:
        # For non-finite numbers NaN, INF and -INF
        # the constraint always is not satisfied
        return False
    return False


def check_pattern(constraint, cell):
    if cell is None:
        return True
    match = constraint.match(cell)
    if match:
        return True
    return False


def check_enum(constraint, cell):
    if cell is None:
        return True
    if cell in constraint:
        return True
    return False


COMPILED_RE = type(re.compile(""))
