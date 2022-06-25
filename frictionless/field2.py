from __future__ import annotations
import re
import decimal
from functools import partial
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, List
from .metadata2 import Metadata2
from .system import system
from . import settings
from . import helpers
from . import errors

if TYPE_CHECKING:
    from .schema import Schema


@dataclass
class Field2(Metadata2):
    """Field representation"""

    type: str = field(init=False)
    builtin: bool = field(init=False, default=False)
    supported_constraints: List[str] = field(init=False, default_factory=list)

    # Properties

    format: str = settings.DEFAULT_FIELD_FORMAT
    """TODO: add docs"""

    name: Optional[str] = None
    """TODO: add docs"""

    title: Optional[str] = None
    """TODO: add docs"""

    description: Optional[str] = None
    """TODO: add docs"""

    @property
    def description_html(self):
        """TODO: add docs"""
        return helpers.md_to_html(self.description)

    @property
    def description_text(self):
        """TODO: add docs"""
        return helpers.html_to_text(self.description_html)

    example: Optional[str] = None
    """TODO: add docs"""

    missing_values: List[str] = field(
        default_factory=settings.DEFAULT_MISSING_VALUES.copy
    )
    """TODO: add docs"""

    constraints: dict = field(default_factory=dict)
    """TODO: add docs"""

    @property
    def required(self):
        """TODO: add docs"""
        return self.constraints.get("required", False)

    @required.setter
    def required(self, value: bool):
        self.constraints["requied"] = value

    rdf_type: Optional[str] = None
    """TODO: add docs"""

    # TODO: recover
    schema: Optional[Schema] = None
    """TODO: add docs"""

    # Read

    def read_cell(self, cell):
        cell_reader = self.create_cell_reader()
        return cell_reader(cell)

    def read_value(self, cell):
        value_reader = self.create_value_reader()
        return value_reader(cell)

    def create_cell_reader(self):
        value_reader = self.create_value_reader()

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
            notes = {}
            if cell in self.missing_values:
                cell = None
            if cell is not None:
                cell = value_reader(cell)
                if cell is None:
                    notes["type"] = f'type is "{self.type}/{self.format}"'
            if not notes and checks:
                for name, check in checks.items():
                    if not check(cell):
                        constraint = self.constraints[name]
                        notes[name] = f'constraint "{name}" is "{constraint}"'
            return cell, notes

        return cell_reader

    def create_value_reader(self):
        raise NotImplementedError()

    # Write

    def write_cell(self, cell):
        cell_writer = self.create_cell_writer()
        return cell_writer(cell)

    def write_value(self, cell):
        value_writer = self.create_value_writer()
        return value_writer(cell)

    def create_cell_writer(self):
        value_writer = self.create_value_writer()

        # Create missing value
        missing_value = settings.DEFAULT_MISSING_VALUES[0]
        if self.missing_values:
            missing_value = self.missing_values[0]

        # Create writer
        def cell_writer(cell, *, ignore_missing=False):
            notes = {}
            if cell is None:
                cell = cell if ignore_missing else missing_value
                return cell, notes
            cell = value_writer(cell)
            if cell is None:
                notes["type"] = f'type is "{self.type}/{self.format}"'
            return cell, notes

        return cell_writer

    def create_value_writer(self):
        raise NotImplementedError()

    # Convert

    # TODO: review
    @classmethod
    def from_descriptor(cls, descriptor):
        if cls is Field2:
            descriptor = cls.metadata_normalize(descriptor)
            return system.create_field(descriptor)  # type: ignore
        return super().from_descriptor(descriptor)

    # Metadata

    metadata_Error = errors.FieldError
    metadata_profile = settings.SCHEMA_PROFILE["properties"]["fields"]["items"]

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Constraints
        for name in self.constraints.keys():
            if name not in self.supported_constraints + ["unique"]:
                note = f'constraint "{name}" is not supported by type "{self.type}"'
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
