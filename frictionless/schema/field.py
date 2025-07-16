from __future__ import annotations

import copy
import decimal
import re
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Optional, Pattern

import attrs
import pydantic

from .. import errors, settings
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..system import system
from .field_descriptor import BooleanFieldDescriptor, FieldDescriptor

if TYPE_CHECKING:
    from ..types import IDescriptor
    from . import types
    from .schema import Schema


@attrs.define(kw_only=True, repr=False)
class Field(Metadata):
    """Field representation"""

    _descriptor: Optional[FieldDescriptor] = None

    name: str
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters.
    """

    type: ClassVar[str]
    """
    Type of the field such as "boolean", "integer" etc.
    """

    title: Optional[str] = None
    """
    A human-oriented title for the Field.
    """

    description: Optional[str] = None
    """
    A brief description of the Field.
    """

    format: str = settings.DEFAULT_FIELD_FORMAT
    """
    Format of the field to specify different value readers for the field type.
    For example: "default","array" etc.
    """

    missing_values: List[str] = attrs.field(factory=settings.DEFAULT_MISSING_VALUES.copy)
    """
    List of string values to be set as missing values in the field. If any of string in missing values
    is found in the field value then it is set as None.
    """

    constraints: Dict[str, Any] = attrs.field(factory=dict)
    """
    A dictionary with rules that constraints the data value permitted for a field.
    """

    rdf_type: Optional[str] = None
    """
    RDF type. Indicates whether the field is of RDF type.
    """

    example: Optional[str] = None
    """
    An example of a value for the field.
    """

    schema: Optional[Schema] = None
    """
    Schema class of which the field is part of.
    """

    builtin: ClassVar[bool] = False
    """
    Specifies if field is the builtin feature.
    """

    supported_constraints: ClassVar[List[str]] = []
    """
    List of supported constraints for a field.
    """

    def __setattr__(self, name: str, value: Any):  # type: ignore
        if name == "type":
            note = 'Use "schema.set_field_type()" to update the type of the field'
            raise FrictionlessException(errors.FieldError(note=note))
        return super().__setattr__(name, value)  # type: ignore

    @property
    def required(self):
        """Indicates if field is mandatory."""
        return self.constraints.get("required", False)

    @required.setter
    def required(self, value: bool):
        self.constraints["required"] = value

    # Read

    def read_cell(self, cell: Any):
        cell_reader = self.create_cell_reader()
        return cell_reader(cell)

    def create_cell_reader(self) -> types.ICellReader:
        value_reader = self.create_value_reader()

        # Create missing values
        missing_values = self.missing_values
        if not self.has_defined("missing_values") and self.schema:
            missing_values = self.schema.missing_values

        # TODO: review where we need to cast constraints
        # Create checks
        checks: Dict[str, Callable[[Any], bool]] = {}
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
        def cell_reader(cell: Any):
            notes: Optional[Dict[str, str]] = None
            if str(cell) in missing_values:
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

    def create_value_reader(self) -> types.IValueReader:
        # Create reader
        def value_reader(cell: Any):
            if self._descriptor and isinstance(self._descriptor, BooleanFieldDescriptor):
                return self._descriptor.read_value(cell)
            return cell

        return value_reader

    # Write

    def write_cell(self, cell: Any, *, ignore_missing: bool = False):
        cell_writer = self.create_cell_writer()
        return cell_writer(cell, ignore_missing=ignore_missing)

    def create_cell_writer(self) -> types.ICellWriter:
        value_writer = self.create_value_writer()

        # Create missing value
        try:
            missing_value = self.missing_values[0]
            if not self.has_defined("missing_values") and self.schema:
                missing_value = self.schema.missing_values[0]
        except IndexError:
            missing_value = settings.DEFAULT_MISSING_VALUES[0]

        # Create writer
        def cell_writer(cell: Any, *, ignore_missing: bool = False):
            notes: Optional[Dict[str, str]] = None
            if cell is None:
                cell = cell if ignore_missing else missing_value
                return cell, notes
            cell = value_writer(cell)
            if cell is None:
                notes = notes or {}
                notes["type"] = f'type is "{self.type}/{self.format}"'
            return cell, notes

        return cell_writer

    def create_value_writer(self) -> types.IValueWriter:
        # Create writer
        def value_writer(cell: Any):
            if self._descriptor and isinstance(self._descriptor, BooleanFieldDescriptor):
                return self._descriptor.write_value(cell)
            return str(cell)

        return value_writer

    # Metadata

    metadata_type = "field"
    metadata_Error = errors.FieldError
    metadata_profile = {
        "type": "object",
        "required": ["name"],
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
    def metadata_select_class(cls, type: Optional[str]):
        return system.select_field_class(type or settings.DEFAULT_FIELD_TYPE_SPECS_V1)

    @classmethod
    def metadata_transform(cls, descriptor: IDescriptor):
        super().metadata_transform(descriptor)

        # Format (standards/v1)
        format = descriptor.get("format")
        if format and isinstance(format, str) and format.startswith("fmt:"):
            descriptor["format"] = format.replace("fmt:", "")

    @classmethod
    def metadata_import(
        cls,
        descriptor: IDescriptor,
        *,
        with_basepath: bool = False,
        **options: Any,
    ) -> "Field":
        descriptor_copy = copy.deepcopy(descriptor)
        field = super().metadata_import(
            descriptor,
            with_basepath=with_basepath,
        )

        if field.type == "boolean":
            try:
                field._descriptor = BooleanFieldDescriptor.model_validate(descriptor_copy)
            except pydantic.ValidationError as ve:
                error = errors.SchemaError(note=str(ve))
                raise FrictionlessException(error)

        return field

    def to_descriptor(self, *, validate: bool = False) -> IDescriptor:
        if self._descriptor and isinstance(self._descriptor, BooleanFieldDescriptor):
            descr = self._descriptor.model_dump(exclude_none=True, exclude_unset=True)
            ## Temporarily, Field properties have priority over
            ## Field._descriptor properties
            descr = {**descr, **super().to_descriptor(validate=validate)}
            return descr
        else:
            return super().to_descriptor(validate=validate)

    @classmethod
    def metadata_validate(cls, descriptor: IDescriptor):  # type: ignore
        metadata_errors = list(super().metadata_validate(descriptor))
        if metadata_errors:
            yield from metadata_errors
            return

        # Constraints
        for name in descriptor.get("constraints", {}):
            if name not in cls.supported_constraints + ["unique"]:
                note = f'constraint "{name}" is not supported by type "{cls.type}"'
                yield errors.FieldError(note=note)

        # Examples
        example = descriptor.get("example")
        if example:
            type = descriptor.get("type")
            Class = system.select_field_class(type)

            field = Class(
                name=descriptor.get("name"),  # type: ignore
                format=descriptor.get("format", "default"),
            )

            if type == "boolean":
                # 'example' value must be compared to customized 'trueValues' and 'falseValues'
                if "trueValues" in descriptor.keys():
                    field.true_values = descriptor["trueValues"]
                if "falseValues" in descriptor.keys():
                    field.false_values = descriptor["falseValues"]
            _, notes = field.read_cell(example)
            if notes is not None:
                note = f'example value "{example}" for field "{field.name}" is not valid'
                yield errors.FieldError(note=note)

        # Misleading
        for name in ["required"]:
            if name in descriptor:
                note = f'"{name}" should be set as "constraints.{name}"'
                yield errors.FieldError(note=note)


# Internal


def check_required(constraint: bool, cell: Any):
    if not (constraint and cell is None):
        return True
    return False


def check_minLength(constraint: Any, cell: Any):
    if cell is None:
        return True
    if len(cell) >= constraint:
        return True
    return False


def check_maxLength(constraint: Any, cell: Any):
    if cell is None:
        return True
    if len(cell) <= constraint:
        return True
    return False


def check_minimum(constraint: Any, cell: Any):
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


def check_maximum(constraint: Any, cell: Any):
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


def check_pattern(constraint: Pattern[str], cell: Optional[str]):
    if cell is None:
        return True
    match = constraint.match(cell)
    if match:
        return True
    return False


def check_enum(constraint: List[Any], cell: Any):
    if cell is None:
        return True
    if cell in constraint:
        return True
    return False


COMPILED_RE = type(re.compile(""))
