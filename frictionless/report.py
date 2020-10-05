import functools
from copy import deepcopy
from . import config
from . import helpers
from . import exceptions
from .metadata import Metadata
from .errors import Error, TaskError, ReportError


class Report(Metadata):
    """Report representation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Report`

    Parameters:
        descriptor? (str|dict): report descriptor
        time (float): validation time
        errors (Error[]): validation errors
        tables (ReportTable[]): validation tables

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, time, errors, tables):
        self["version"] = config.VERSION
        self["time"] = time
        self["valid"] = not errors and all(tab["valid"] for tab in tables)
        self["stats"] = {
            "errors": len(errors) + sum(tab["stats"]["errors"] for tab in tables),
            "tables": len(tables),
        }
        self["errors"] = errors
        self["tables"] = tables
        super().__init__(descriptor)

    @property
    def version(self):
        """
        Returns:
            str: frictionless version
        """
        return self["version"]

    @property
    def time(self):
        """
        Returns:
            float: validation time
        """
        return self["time"]

    @property
    def valid(self):
        """
        Returns:
            bool: validation result
        """
        return self["valid"]

    @property
    def stats(self):
        """
        Returns:
            dict: validation stats
        """
        return self["stats"]

    @property
    def errors(self):
        """
        Returns:
            Error[]: validation errors
        """
        return self["errors"]

    @property
    def tables(self):
        """
        Returns:
            ReportTable[]: validation tables
        """
        return self["tables"]

    @property
    def table(self):
        """
        Returns:
            ReportTable: validation table (if there is only one)

        Raises:
            FrictionlessException: if there are more that 1 table
        """
        if len(self.tables) != 1:
            error = Error(note='The "report.table" is available for single table reports')
            raise exceptions.FrictionlessException(error)
        return self.tables[0]

    # Expand

    def expand(self):
        """Expand metadata"""
        for table in self.tables:
            table.expand()

    # Flatten

    def flatten(self, spec):
        """Flatten the report

        Parameters
            spec (any[]): flatten specification

        Returns:
            any[]: flatten report
        """
        result = []
        for error in self.errors:
            context = {}
            context.update(error)
            result.append([context.get(prop) for prop in spec])
        for count, table in enumerate(self.tables, start=1):
            for error in table.errors:
                context = {"tableNumber": count, "tablePosition": count}
                context.update(error)
                result.append([context.get(prop) for prop in spec])
        return result

    # Import/Export

    @staticmethod
    def from_validate(validate):
        """Validate function wrapper

        Parameters:
            validate (func): validate

        Returns:
            func: wrapped validate
        """

        @functools.wraps(validate)
        def wrapper(*args, **kwargs):
            timer = helpers.Timer()
            try:
                return validate(*args, **kwargs)
            except Exception as exception:
                error = TaskError(note=str(exception))
                if isinstance(exception, exceptions.FrictionlessException):
                    error = exception.error
                return Report(time=timer.time, errors=[error], tables=[])

        return wrapper

    # Metadata

    metadata_strict = True
    metadata_Error = ReportError
    metadata_profile = deepcopy(config.REPORT_PROFILE)
    metadata_profile["properties"]["tables"] = {
        "type": "array",
        "items": {"type": "object"},
    }

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Tables
        for table in self.tables:
            yield from table.metadata_errors


class ReportTable(Metadata):
    """Report table representation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import ReportTable`

    Parameters:
        descriptor? (str|dict): schema descriptor
        time (float): validation time
        scope (str[]): validation scope
        partial (bool): wehter validation was partial
        errors (Error[]): validation errors
        table (Table): validation table

    # Raises
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, time, scope, partial, errors, table):
        # File
        # TODO: review path/data/source logic
        self["path"] = table.path or "memory"
        self["scheme"] = table.scheme
        self["format"] = table.format
        self["hashing"] = table.hashing
        self["encoding"] = table.encoding
        self["compression"] = table.compression
        self["compressionPath"] = table.compression_path
        # Table
        self["dialect"] = table.dialect
        self["query"] = table.query
        self.setinitial("header", table.header)
        self.setinitial("schema", table.schema)
        # Validation
        self["time"] = time
        self["valid"] = not errors
        self["scope"] = scope
        self["stats"] = helpers.copy_merge(table.stats, {"errors": len(errors)})
        self["partial"] = partial
        self["errors"] = errors
        super().__init__(descriptor)

    @property
    def path(self):
        """
        Returns:
            str: path
        """
        return self["path"]

    @property
    def scheme(self):
        """
        Returns:
            str: scheme
        """
        return self["scheme"]

    @property
    def format(self):
        """
        Returns:
            str: format
        """
        return self["format"]

    @property
    def hashing(self):
        """
        Returns:
            str: hashing
        """
        return self["hashing"]

    @property
    def encoding(self):
        """
        Returns:
            str: encoding
        """
        return self["encoding"]

    @property
    def compression(self):
        """
        Returns:
            str: compression
        """
        return self["compression"]

    @property
    def compression_path(self):
        """
        Returns:
            str: compression path
        """
        return self["compressionPath"]

    @property
    def dialect(self):
        """
        Returns:
            Dialect: dialect
        """
        return self["dialect"]

    @property
    def query(self):
        """
        Returns:
            Query: query
        """
        return self["query"]

    @property
    def header(self):
        """
        Returns:
            Header: header
        """
        return self["header"]

    @property
    def schema(self):
        """
        Returns:
            Schema: schema
        """
        return self["schema"]

    @property
    def time(self):
        """
        Returns:
            float: validation time
        """
        return self["time"]

    @property
    def valid(self):
        """
        Returns:
            bool: validation result
        """
        return self["valid"]

    @property
    def scope(self):
        """
        Returns:
            str[]: validation scope
        """
        return self["scope"]

    @property
    def stats(self):
        """
        Returns:
            dict: validation stats
        """
        return self["stats"]

    @property
    def partial(self):
        """
        Returns:
            bool: if validation partial
        """
        return self["partial"]

    @property
    def errors(self):
        """
        Returns:
            Error[]: validation errors
        """
        return self["errors"]

    @property
    def error(self):
        """
        Returns:
            Error: validation error if there is only one

        Raises:
            FrictionlessException: if more than one errors
        """
        if len(self.errors) != 1:
            error = Error(note='The "table.error" is available for single error tables')
            raise exceptions.FrictionlessException(error)
        return self.errors[0]

    # Expand

    def expand(self):
        """Expand metadata"""
        self.dialect.expand()
        if self.schema is not None:
            self.schema.expand()

    # Flatten

    def flatten(self, spec):
        """Flatten the report

        Parameters
            spec (any[]): flatten specification

        Returns:
            any[]: flatten table report
        """
        result = []
        for error in self.errors:
            context = {}
            context.update(error)
            result.append([context.get(prop) for prop in spec])
        return result

    # Metadata

    metadata_strict = True
    metadata_Error = ReportError
    metadata_profile = config.REPORT_PROFILE["properties"]["tables"]["items"]
