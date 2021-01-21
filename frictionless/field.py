import re
import decimal
import warnings
from copy import copy
from operator import setitem
from functools import partial
from collections import OrderedDict
from .exception import FrictionlessException
from .metadata import Metadata
from .system import system
from . import errors
from . import config
from . import types


class Field(Metadata):
    """Field representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Field`

    Parameters:
        descriptor? (str|dict): field descriptor
        name? (str): field name (for machines)
        title? (str): field title (for humans)
        descriptor? (str): field descriptor
        type? (str): field type e.g. `string`
        format? (str): field format e.g. `default`
        missing_values? (str[]): missing values
        constraints? (dict): constraints
        rdf_type? (str): RDF type
        schema? (Schema): parent schema object

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor=None,
        *,
        name=None,
        title=None,
        description=None,
        type=None,
        format=None,
        missing_values=None,
        constraints=None,
        rdf_type=None,
        schema=None,
    ):
        self.setinitial("name", name)
        self.setinitial("title", title)
        self.setinitial("description", description)
        self.setinitial("type", type)
        self.setinitial("format", format)
        self.setinitial("missingValues", missing_values)
        self.setinitial("constraints", constraints)
        self.setinitial("rdfType", rdf_type)
        self.__schema = schema
        self.__type = None
        super().__init__(descriptor)

        # Replace deprecated "fmt:"
        format = self.get("format")
        if format and isinstance(format, str) and format.startswith("fmt:"):
            message = 'Format "fmt:<PATTERN>" is deprecated. Please remove "fmt:" prefix.'
            warnings.warn(message, UserWarning)
            self["format"] = format.replace("fmt:", "")

    @Metadata.property
    def name(self):
        """
        Returns:
            str: name
        """
        return self.get("name", self.type)

    @Metadata.property
    def title(self):
        """
        Returns:
            str?: title
        """
        return self.get("title")

    @Metadata.property
    def description(self):
        """
        Returns:
            str?: description
        """
        return self.get("description")

    @Metadata.property
    def type(self):
        """
        Returns:
            str: type
        """
        return self.get("type", "any")

    @Metadata.property
    def format(self):
        """
        Returns:
            str: format
        """
        format = self.get("format", "default")
        return format

    @Metadata.property
    def missing_values(self):
        """
        Returns:
            str[]: missing values
        """
        schema = self.__schema
        default = schema.missing_values if schema else copy(config.DEFAULT_MISSING_VALUES)
        missing_values = self.get("missingValues", default)
        return self.metadata_attach("missingValues", missing_values)

    @Metadata.property
    def constraints(self):
        """
        Returns:
            dict: constraints
        """
        constraints = self.get("constraints", {})
        return self.metadata_attach("constraints", constraints)

    @Metadata.property
    def rdf_type(self):
        """
        Returns:
            str?: RDF Type
        """
        return self.get("rdfType")

    @Metadata.property(
        write=lambda self, value: setitem(self.constraints, "required", value)
    )
    def required(self):
        """
        Returns:
            bool: if field is requried
        """
        return self.constraints.get("required", False)

    @property
    def schema(self):
        """
        Returns:
            Schema?: parent schema
        """
        return self.__schema

    # Boolean

    @Metadata.property
    def true_values(self):
        """
        Returns:
            str[]: true values
        """
        true_values = self.get("trueValues", config.DEFAULT_TRUE_VALUES)
        return self.metadata_attach("trueValues", true_values)

    @Metadata.property
    def false_values(self):
        """
        Returns:
            str[]: false values
        """
        false_values = self.get("falseValues", config.DEFAULT_FALSE_VALUES)
        return self.metadata_attach("falseValues", false_values)

    # Integer/Number

    @Metadata.property
    def bare_number(self):
        """
        Returns:
            bool: if a bare number
        """
        return self.get("bareNumber", config.DEFAULT_BARE_NUMBER)

    @Metadata.property
    def float_number(self):
        """
        Returns:
            bool: whether it's a floating point number
        """
        return self.get("floatNumber", config.DEFAULT_FLOAT_NUMBER)

    @Metadata.property
    def decimal_char(self):
        """
        Returns:
            str: decimal char
        """
        return self.get("decimalChar", config.DEFAULT_DECIMAL_CHAR)

    @Metadata.property
    def group_char(self):
        """
        Returns:
            str: group char
        """
        return self.get("groupChar", config.DEFAULT_GROUP_CHAR)

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("name", "field")
        self.setdefault("type", "any")
        self.setdefault("format", "default")

        # Boolean
        if self.type == "boolean":
            self.setdefault("trueValues", self.true_values)
            self.setdefault("falseValues", self.false_values)

        # Integer/Number
        if self.type in ["integer", "number"]:
            self.setdefault("bareNumber", self.bare_number)
            if self.type == "number":
                self.setdefault("decimalChar", self.decimal_char)
                self.setdefault("groupChar", self.group_char)

    # Read

    def read_cell(self, cell):
        """Read cell

        Parameters:
            cell (any): cell

        Returns:
            (any, OrderedDict): processed cell and dict of notes

        """
        notes = None
        if cell in self.missing_values:
            cell = None
        if cell is not None:
            cell = self.__type.read_cell(cell)
            if cell is None:
                notes = notes or OrderedDict()
                notes["type"] = f'type is "{self.type}/{self.format}"'
        if not notes and self.read_cell_checks:
            for name, check in self.read_cell_checks.items():
                if not check(cell):
                    notes = notes or OrderedDict()
                    notes[name] = f'constraint "{name}" is "{self.constraints[name]}"'
        return cell, notes

    def read_cell_convert(self, cell):
        """Read cell (convert only)

        Parameters:
            cell (any): cell

        Returns:
            any/None: processed cell or None if an error

        """
        return self.__type.read_cell(cell)

    @Metadata.property(write=False)
    def read_cell_checks(self):
        """Read cell (checks only)

        Returns:
            OrderedDict: dictionlary of check function by a constraint name

        """
        checks = OrderedDict()
        for name in self.__type.constraints:
            constraint = self.constraints.get(name)
            if constraint is not None:
                if name in ["minimum", "maximum"]:
                    constraint = self.__type.read_cell(constraint)
                if name == "enum":
                    constraint = list(map(self.__type.read_cell, constraint))
                checks[name] = partial(globals().get(f"check_{name}"), constraint)
        return checks

    # Write

    def write_cell(self, cell, *, ignore_missing=False):
        """Write cell

        Parameters:
            cell (any): cell to convert
            ignore_missing? (bool): don't convert None values

        Returns:
            (any, OrderedDict): processed cell and dict of notes

        """
        notes = None
        if cell is None:
            missing_value = cell if ignore_missing else self.write_cell_missing_value
            return missing_value, notes
        cell = self.__type.write_cell(cell)
        if cell is None:
            notes = notes or OrderedDict()
            notes["type"] = f'type is "{self.type}/{self.format}"'
        return cell, notes

    def write_cell_convert(self, cell):
        """Write cell (convert only)

        Parameters:
            cell (any): cell

        Returns:
            any/None: processed cell or None if an error

        """
        return self.__type.write_cell(cell)

    @Metadata.property(write=False)
    def write_cell_missing_value(self):
        """Write cell (missing value only)

        Returns:
            str: a value to replace None cells

        """
        if self.missing_values:
            return self.missing_values[0]
        return config.DEFAULT_MISSING_VALUES[0]

    # Metadata

    def metadata_process(self):

        # Type
        try:
            self.__type = system.create_type(self)
        except FrictionlessException:
            self.__type = types.AnyType(self)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Constraints
        for name in self.constraints.keys():
            if name not in self.__type.constraints + ["unique"]:
                note = f'constraint "{name}" is not supported by type "{self.type}"'
                yield errors.SchemaError(note=note)

    # Metadata

    metadata_Error = errors.FieldError  # type: ignore
    metadata_profile = config.SCHEMA_PROFILE["properties"]["fields"]["items"]
    metadata_duplicate = True


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
    if not isinstance(constraint, COMPILED_RE):
        regex = re.compile("^{0}$".format(constraint))
    else:
        regex = constraint
    match = regex.match(cell)
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
