from __future__ import annotations

import copy
import decimal
import re
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Optional, Pattern, Type

import attrs
import pydantic
from pydantic import BaseModel

from .. import errors, settings
from ..exception import FrictionlessException
# from ..fields.boolean_descriptor import BooleanFieldDescriptor
# from ..fields.date_descriptor import DateFieldDescriptor
# from ..fields.integer_descriptor import IntegerFieldDescriptor
from ..fields.field_descriptor import (
    AnyFieldDescriptor,
    ArrayFieldDescriptor,
    BooleanFieldDescriptor,
    DateFieldDescriptor,
    DatetimeFieldDescriptor,
    DurationFieldDescriptor,
    FieldDescriptor,
    GeoJSONFieldDescriptor,
    GeoPointFieldDescriptor,
    IntegerFieldDescriptor,
    NumberFieldDescriptor,
    ObjectFieldDescriptor,
    StringFieldDescriptor,
    TimeFieldDescriptor,
    YearFieldDescriptor,
    YearmonthFieldDescriptor,
)
from ..metadata import Metadata
from ..system import system

if TYPE_CHECKING:
    from ..types import IDescriptor
    from . import types
    from .schema import Schema

# Mapping from field type to its corresponding descriptor class
TYPE_TO_DESCRIPTOR: Dict[str, Type[BaseModel]] = {
    "any": AnyFieldDescriptor,
    "array": ArrayFieldDescriptor,
    "boolean": BooleanFieldDescriptor,
    "date": DateFieldDescriptor,
    "datetime": DatetimeFieldDescriptor,
    "duration": DurationFieldDescriptor,
    "geojson": GeoJSONFieldDescriptor,
    "geopoint": GeoPointFieldDescriptor,
    "integer": IntegerFieldDescriptor,
    "number": NumberFieldDescriptor,
    "object": ObjectFieldDescriptor,
    "string": StringFieldDescriptor,
    "time": TimeFieldDescriptor,
    "year": YearFieldDescriptor,
    "yearmonth": YearmonthFieldDescriptor,
}

# Descriptor integration (temporary, during Field refactor)
# Used at two points:
# - Sync (runtime): when a Field attribute changes, update the pydantic _descriptor so read_cell/write_cell use up-to-date parsing logic (e.g. format="email").
# - Init (validation): when creating _descriptor, we pass a dict using Frictionless descriptor keys (camelCase aliases)
DESCRIPTOR_INIT_ALIASES: Dict[str, str] = {
    "format": "format",
    "decimal_char": "decimalChar",
    "group_char": "groupChar",
    "bare_number": "bareNumber",
    "float_number": "floatNumber",
    "true_values": "trueValues",
    "false_values": "falseValues",
}

DESCRIPTOR_SYNC_ATTRS: set[str] = { *DESCRIPTOR_INIT_ALIASES.keys() }

@attrs.define(kw_only=True, repr=False)
class Field(Metadata):
    """Field representation"""

    _descriptor: Optional[ FieldDescriptor] = None

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

    # All optional fields for the field descriptor
    decimal_char: Optional[str] = None
    group_char: Optional[str] = None
    bare_number: Optional[bool] = None
    float_number: Optional[bool] = None
    true_values: Optional[List[str]] = None
    false_values: Optional[List[str]] = None

    def __attrs_post_init__(self):
        self._init_descriptor_from_field()

    def __setattr__(self, name: str, value: Any):  # type: ignore
        if name == "type":
            note = 'Use "schema.set_field_type()" to update the type of the field'
            raise FrictionlessException(errors.FieldError(note=note))
        
        result = super().__setattr__(name, value)  # type: ignore

        self._sync_descriptor_property(name, value)
        
        return result

    def _sync_descriptor_property(self, name: str, value: Any) -> None:
        """Keep the internal pydantic descriptor in sync with Field attribute assignments."""
        if name not in DESCRIPTOR_SYNC_ATTRS:
            return

        if name == "format" and isinstance(value, str):
            # Don't sync implicit default format into pydantic, so that it doesnt become "set" and get exported by "model_dump(exclude_unset=True)".
            if not self._should_include_format():
                return

        if self._descriptor is None and hasattr(self, "type") and self.type:
            self._init_descriptor_from_field()

        if self._descriptor and hasattr(self._descriptor, name):
            setattr(self._descriptor, name, value)
    
    def _init_descriptor_from_field(self) -> None:
        """Initialize _descriptor from Field properties if not already set
        Use camelCase keys for descriptor init (as per Frictionless descriptor keys)
        """
        if self._descriptor is not None:
            return
        
        if not hasattr(self, "type") or not self.type:
            return

        descriptor_class = TYPE_TO_DESCRIPTOR.get(self.type)
        if not descriptor_class:
            return
        
        descriptor_dict: Dict[str, Any] = {
            "name": self.name,
            "type": self.type,
        }

        for attr, alias in DESCRIPTOR_INIT_ALIASES.items():
            if attr == "format":
                if self._should_include_format():
                    descriptor_dict["format"] = self.format
                continue
            value = getattr(self, attr, None)
            if value is not None:
                descriptor_dict[alias] = value
        
        try:
            self._descriptor = descriptor_class.model_validate(descriptor_dict)  # type: ignore
        except pydantic.ValidationError:
            self._descriptor = None

    def _should_include_format(self) -> bool:
        """Whether `format` should be considered set for descriptor/init/sync purposes."""
        fmt = getattr(self, "format", None)
        if not isinstance(fmt, str) or not fmt:
            return False
        return self.has_defined("format") or fmt != settings.DEFAULT_FIELD_FORMAT

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
        def value_reader(cell: Any) -> Any:
            if self._descriptor:
                return self._descriptor.read_value(cell)  # type: ignore
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
        def value_writer(cell: Any) -> Any:
            if self._descriptor:
                return self._descriptor.write_value(cell)  # type: ignore
            return cell

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

        # Get the descriptor class for this field type
        field_type = field.type
        DescriptorClass = TYPE_TO_DESCRIPTOR.get(field_type) if field_type else None

        if DescriptorClass:
            try:
                field._descriptor = DescriptorClass.model_validate(descriptor_copy)  # type: ignore
            except pydantic.ValidationError as ve:
                # Temporary: Handle Pydantic validation errors
                # TODO: Remove once Pydantic validation is properly integrated
                handle_pydantic_error_for_import(ve)

        return field

    def to_descriptor(self, *, validate: bool = False) -> IDescriptor:
        if self._descriptor and isinstance(
            self._descriptor, (AnyFieldDescriptor, BooleanFieldDescriptor, IntegerFieldDescriptor, DateFieldDescriptor, DatetimeFieldDescriptor, DurationFieldDescriptor, GeoJSONFieldDescriptor, GeoPointFieldDescriptor, NumberFieldDescriptor, ObjectFieldDescriptor, StringFieldDescriptor, TimeFieldDescriptor, YearFieldDescriptor, YearmonthFieldDescriptor)
        ):
            base_descr = super().to_descriptor(validate=validate)
            # Set by_alias=True to get camelCase keys used by Frictionless (bareNumber) instead of snake_case (bare_number)
            # Exclude 'name' from descriptor_descr because it may be "shared" (coming from detector.py)
            descriptor_descr = self._descriptor.model_dump(
                exclude_none=True, exclude_unset=True, by_alias=True, exclude={"name"}
            )
            ## Temporarily, Field properties have priority over
            ## Field._descriptor properties
            ## Merge descriptor_descr into base_descr to preserve base order
            descr = {**base_descr, **descriptor_descr}
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
            # Validate descriptor with Pydantic before continuing
            # This catches Pydantic validation errors (e.g., invalid example values)
            type = descriptor.get("type")
            DescriptorClass = TYPE_TO_DESCRIPTOR.get(type) if type else None
            if DescriptorClass:
                try:
                    DescriptorClass.model_validate(descriptor)
                except pydantic.ValidationError as ve:
                    # Temporary: Handle Pydantic validation errors
                    # TODO: Remove once Pydantic validation is properly integrated
                    field_errors = handle_pydantic_error_for_validate(ve)
                    for field_error in field_errors:
                        yield field_error
                    return
            
            # Use metadata_select_class + metadata_import directly (without validation) to avoid recursion
            # This properly initializes the field with all properties including
            # type-specific ones like trueValues/falseValues for boolean
            # We need to pass a copy of the descriptor to avoid modifying the original
            Class = Field.metadata_select_class(type)
            descriptor_copy = copy.deepcopy(descriptor)
            field = Class.metadata_import(descriptor_copy)
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


# Temporary Pydantic error handling functions
# TODO: Remove these once Pydantic validation is properly integrated
# These functions centralize the parsing logic to make future removal easier

def parse_pydantic_errors(ve: pydantic.ValidationError) -> List[str]:
    """Parse Pydantic validation errors into clean error messages.
    
    This is a temporary function to handle Pydantic ValidationError objects
    and convert them to clean error messages by removing Pydantic-specific prefixes.
    
    Args:
        ve: A Pydantic ValidationError
        
    Returns:
        A list of cleaned error messages (with "Value error, " prefix removed)
    """
    error_messages: List[str] = []
    for err in ve.errors():
        if "msg" in err:
            note: str = str(err["msg"])
            # Remove "Value error, " prefix if present (Pydantic-specific formatting)
            note = note.replace("Value error, ", "")
            error_messages.append(note)
    return error_messages


def handle_pydantic_error_for_import(ve: pydantic.ValidationError) -> None:
    """Handle Pydantic ValidationError in metadata_import context.
    
    This is a temporary function that converts Pydantic validation errors
    into Frictionless SchemaError exceptions for use during field import.
    
    Args:
        ve: A Pydantic ValidationError
        
    Raises:
        FrictionlessException with a SchemaError containing the first error message
    """
    error_messages = parse_pydantic_errors(ve)
    
    # Use the first error message, or fall back to string representation
    if error_messages:
        error_note = error_messages[0]
    else:
        error_note = str(ve)
    
    error = errors.SchemaError(note=error_note)
    raise FrictionlessException(error)


def handle_pydantic_error_for_validate(ve: pydantic.ValidationError) -> List[errors.FieldError]:
    """Handle Pydantic ValidationError in metadata_validate context.
    
    This is a temporary function that converts Pydantic validation errors
    into Frictionless FieldError objects for use during field validation.
    
    Args:
        ve: A Pydantic ValidationError
        
    Returns:
        A list of FieldError objects, one for each error message
    """
    error_messages = parse_pydantic_errors(ve)
    return [errors.FieldError(note=note) for note in error_messages]


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
