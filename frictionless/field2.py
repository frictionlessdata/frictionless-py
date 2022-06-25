from __future__ import annotations
import re
import decimal
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, List
from .metadata2 import Metadata2
from . import settings
from . import helpers
from . import errors

if TYPE_CHECKING:
    from .schema import Schema


@dataclass
class Field(Metadata2):
    """Field representation"""

    type: str
    builtin = False
    supported_constraints: List[str] = field(default_factory=list)

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

    schema: Optional[Schema] = None
    """TODO: add docs"""

    # Read

    def create_cell_reader(self):
        pass

    # Write

    def create_cell_writer(self):
        pass

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
