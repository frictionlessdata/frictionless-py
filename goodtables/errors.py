import tabulator
import tableschema
from .metadata import Metadata


class Error(Metadata):
    code = 'error'
    name = 'Error'
    tags = []  # type: ignore
    message = 'Not specified error'
    description = 'Not specified error.'

    def __init__(self):
        self['code'] = self.code
        self['name'] = self.name
        self['tags'] = self.tags
        self['message'] = self.message.format(**self)
        self['description'] = self.description

    def match(self, *, pick_errors, skip_errors):
        match = True
        if pick_errors:
            match = False
            if self['code'] in pick_errors:
                match = True
            if set(self['tags']).intersection(pick_errors):
                match = True
        if skip_errors:
            match = True
            if self['code'] in skip_errors:
                match = False
            if set(self['tags']).intersection(skip_errors):
                match = False
        return match

    @staticmethod
    def from_exception(exception):
        Error = SourceError
        details = str(exception)
        if isinstance(exception, tabulator.exceptions.SourceError):
            Error = SourceError
        elif isinstance(exception, tabulator.exceptions.SchemeError):
            Error = SchemeError
        elif isinstance(exception, tabulator.exceptions.FormatError):
            Error = FormatError
        elif isinstance(exception, tabulator.exceptions.EncodingError):
            Error = EncodingError
        elif isinstance(exception, tabulator.exceptions.CompressionError):
            Error = CompressionError
        elif isinstance(exception, tableschema.exceptions.TableSchemaException):
            Error = SchemaError
        return Error(details=details)

    @staticmethod
    def from_constraint(name, **context):
        Error = None
        if name == 'minLength':
            Error = MinLengthConstraintError
        elif name == 'maxLength':
            Error = MaxLengthConstraintError
        elif name == 'minimum':
            Error = MinimumConstraintError
        elif name == 'maximum':
            Error = MaximumConstraintError
        elif name == 'pattern':
            Error = PatternConstraintError
        elif name == 'enum':
            Error = EnumConstraintError
        else:
            assert name in [
                'minLength',
                'maxLength',
                'minimum',
                'maximum',
                'pattern',
                'enum',
            ]
        return Error(**context)


class ReportError(Error):
    code = 'report-error'
    name = 'Report Error'
    tags = ['#report']
    message = 'The validation report has an error: {details}'
    description = 'A validation cannot be finished.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


# Task


class TaskError(Error):
    code = 'task-error'
    name = 'Task Error'
    tags = ['#task']
    message = 'The validation task has an error: {details}'
    description = 'A validation cannot be processed.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


# Package


class PackageError(Error):
    code = 'package-error'
    name = 'Package Error'
    tags = ['#package']
    message = 'The data package has an error: {details}'
    description = 'A validation cannot be processed.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


# Resource


class ResourceError(Error):
    code = 'resource-error'
    name = 'Resource Error'
    tags = ['#resource']
    message = 'The data resource has an error: {details}'
    description = 'A validation cannot be processed.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


# Table


class SourceError(Error):
    code = 'source-error'
    name = 'Source Error'
    tags = ['#table']
    message = 'The data source has not supported or has inconsistent contents: {details}'
    description = 'Data reading error because of not supported or inconsistent contents.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


class SchemeError(Error):
    code = 'scheme-error'
    name = 'Scheme Error'
    tags = ['#table']
    message = 'The data source could not be successfully loaded: {details}'
    description = 'Data reading error because of incorrect scheme.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


class FormatError(Error):
    code = 'format-error'
    name = 'Format Error'
    tags = ['#table']
    message = 'The data source could not be successfully parsed: {details}'
    description = 'Data reading error because of incorrect format.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


class EncodingError(Error):
    code = 'encoding-error'
    name = 'Encoding Error'
    tags = ['#table']
    message = 'The data source could not be successfully decoded: {details}'
    description = 'Data reading error because of an encoding problem.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


class CompressionError(Error):
    code = 'compression-error'
    name = 'Compression Error'
    tags = ['#table']
    message = 'The data source could not be successfully decompressed: {details}'
    description = 'Data reading error because of a decompression problem.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


class SizeError(Error):
    code = 'size-error'
    name = 'Size Error'
    tags = ['#table', '#integrity']
    message = 'The data source does not match the expected size in bytes: {details}'
    description = 'This error can happen if the data is corrupted.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


class HashError(Error):
    code = 'hash-error'
    name = 'Hash Error'
    tags = ['#table', '#integrity']
    message = 'The data source does not match the expected hash: {details}'
    description = 'This error can happen if the data is corrupted.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


class SchemaError(Error):
    code = 'schema-error'
    name = 'Schema Error'
    tags = ['#table', '#schema']
    message = 'The data source could not be successfully described by the invalid Table Schema: {details}'
    description = 'Provided schema is not valid.'

    def __init__(self, *, details):
        self['details'] = details
        super().__init__()


# Head


class BlankHeaderError(Error):
    code = 'blank-header'
    name = 'Blank Header'
    tags = ['#head', '#structure']
    message = 'Header in field at position {fieldPosition} is blank'
    description = 'A column in the header row is missing a value. Headers should be provided and not be blank.'

    def __init__(self, *, cells, field_name, field_number, field_position):
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        super().__init__()


class DuplicateHeaderError(Error):
    code = 'duplicate-header'
    name = 'Duplicate Header'
    tags = ['#head', '#structure']
    message = 'Header {cell} in field at position {fieldPosition} is duplicated to header in field(s): {details}'
    description = 'Two columns in the header row have the same value. Column names should be unique.'

    def __init__(self, *, cell, cells, field_name, field_number, field_position, details):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        self['details'] = details
        super().__init__()


class ExtraHeaderError(Error):
    code = 'extra-header'
    name = 'Extra Header'
    tags = ['#head', '#schema']
    message = 'There is an extra header {cell} in field at position {fieldPosition}'
    description = 'The first row of the data source contains header that does not exist in the schema.'

    def __init__(self, *, cell, cells, field_position):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldPosition'] = field_position
        super().__init__()


class MissingHeaderError(Error):
    code = 'missing-header'
    name = 'Missing Header'
    tags = ['#head', '#schema']
    message = 'There is a missing header in field {fieldName} at position {fieldPosition}'
    description = 'Based on the schema there should be a header that is missing in the first row of the data source.'

    def __init__(self, *, cell, cells, field_name, field_number, field_position):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        super().__init__()


class NonMatchingHeaderError(Error):
    code = 'non-matching-header'
    name = 'Non-matching Header'
    tags = ['#head', '#schema']
    message = 'Header {cell} in field {fieldName} at position {fieldPosition} does not match the field name in the schema'
    description = 'One of the data source headers does not match the field name defined in the schema.'

    def __init__(self, *, cell, cells, field_name, field_number, field_position):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        super().__init__()


# Body


class BlankRowError(Error):
    code = 'blank-row'
    name = 'Blank Row'
    tags = ['#body', '#structure']
    message = 'Row at position {rowPosition} is completely blank'
    description = 'This row is empty. A row should contain at least one value.'

    def __init__(self, *, row_number, row_position):
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        super().__init__()


class ExtraCellError(Error):
    code = 'extra-cell'
    name = 'Extra Cell'
    tags = ['#body', '#structure']
    message = 'Row at position {rowPosition} has an extra value in field at position {fieldPosition}'
    description = 'This row has more values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.'

    def __init__(self, *, cell, cells, field_position, row_number, row_position):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldPosition'] = field_position
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        super().__init__()


class MissingCellError(Error):
    code = 'missing-cell'
    name = 'Missing Cell'
    tags = ['#body', '#structure']
    message = 'Row at position {rowPosition} has a missing cell in field {fieldName} at position {fieldPosition}'
    description = 'This row has less values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.'

    def __init__(
        self, *, cells, field_name, field_number, field_position, row_number, row_position
    ):
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        super().__init__()


class TypeError(Error):
    code = 'type-error'
    name = 'Missing Cell'
    tags = ['#body', '#schema']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has incompatible type: {details}'
    description = 'The value does not match the schema type and format for this field.'

    def __init__(
        self,
        *,
        cell,
        cells,
        field_name,
        field_number,
        field_position,
        row_number,
        row_position,
        details,
    ):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        self['details'] = details
        super().__init__()


class RequiredConstraintError(Error):
    code = 'required-constraint'
    name = 'Required Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'Field {fieldName} at position {fieldPosition} is a required field, but row at position {rowPosition} has no value'
    description = 'This field is a required field, but it contains no value.'

    def __init__(
        self,
        *,
        cells,
        field_name,
        field_number,
        field_position,
        row_number,
        row_position,
    ):
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        super().__init__()


class MinLengthConstraintError(Error):
    code = 'min-length-constraint'
    name = 'Minimum Length Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the minumum length constraint: {details}'
    description = 'A length of this field value should be greater or equal than schema constraint value.'

    def __init__(
        self,
        *,
        cell,
        cells,
        field_name,
        field_number,
        field_position,
        row_number,
        row_position,
        details,
    ):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        self['details'] = details
        super().__init__()


class MaxLengthConstraintError(Error):
    code = 'max-length-constraint'
    name = 'Maximum Length Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the maximum length constraint: {details}'
    description = 'A length of this field value should be less or equal than schema constraint value.'

    def __init__(
        self,
        *,
        cell,
        cells,
        field_name,
        field_number,
        field_position,
        row_number,
        row_position,
        details,
    ):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        self['details'] = details
        super().__init__()


class MinimumConstraintError(Error):
    code = 'minimum-constraint'
    name = 'Minimum Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the minimum constraint: {details}'
    description = 'This field value should be greater or equal than constraint value.'

    def __init__(
        self,
        *,
        cell,
        cells,
        field_name,
        field_number,
        field_position,
        row_number,
        row_position,
        details,
    ):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        self['details'] = details
        super().__init__()


class MaximumConstraintError(Error):
    code = 'maximum-constraint'
    name = 'Maximum Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the maximum constraint: {details}'
    description = 'This field value should be less or equal than constraint value.'

    def __init__(
        self,
        *,
        cell,
        cells,
        field_name,
        field_number,
        field_position,
        row_number,
        row_position,
        details,
    ):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        self['details'] = details
        super().__init__()


class PatternConstraintError(Error):
    code = 'pattern-constraint'
    name = 'Pattern Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at positin {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the pattern constraint: {details}'
    description = 'This field value should conform to constraint pattern.'

    def __init__(
        self,
        *,
        cell,
        cells,
        field_name,
        field_number,
        field_position,
        row_number,
        row_position,
        details,
    ):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        self['details'] = details
        super().__init__()


class EnumConstraintError(Error):
    code = 'enum-constraint'
    name = 'Enumerable Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at positin {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the given enumeration: {details}'
    description = 'This field value should be equal to one of the values in the enumeration constraint.'

    def __init__(
        self,
        *,
        cell,
        cells,
        field_name,
        field_number,
        field_position,
        row_number,
        row_position,
        details,
    ):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        self['details'] = details
        super().__init__()


class UniqueConstraintError(Error):
    code = 'unique-constraint'
    name = 'Unique Constraint'
    tags = ['#body', '#schema', '#constraint', '#integrity']
    message = 'Row at position {rowPosition} has unique constraint violation in field {fieldName} at position {fieldPosition}: {details}'
    description = 'This field is a unique field but it contains a value that has been used in another row.'

    def __init__(
        self,
        *,
        cell,
        cells,
        field_name,
        field_number,
        field_position,
        row_number,
        row_position,
        details,
    ):
        self['cell'] = cell
        self['cells'] = cells
        self['fieldName'] = field_name
        self['fieldNumber'] = field_number
        self['fieldPosition'] = field_position
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        self['details'] = details
        super().__init__()


class PrimaryKeyError(Error):
    code = 'primary-key-error'
    name = 'Primary Key Error'
    tags = ['#body', '#schema', '#integrity']
    message = 'The row at position {rowPosition} does not conform to the primary key constraint: {details}'
    description = 'Values in the primary key fields should be unique for every row'

    def __init__(
        self, *, cells, row_number, row_position, details,
    ):
        self['cells'] = cells
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        self['details'] = details
        super().__init__()


class ForeignKeyError(Error):
    code = 'foreign-key-error'
    name = 'Foreign Key Error'
    tags = ['#body', '#schema', '#integrity']
    message = 'The row at position {rowPosition} does not conform to the foreign key constraint: {details}'
    description = 'Values in the foreign key fields should exist in the reference table'

    def __init__(
        self, *, cells, row_number, row_position, details,
    ):
        self['cells'] = cells
        self['rowNumber'] = row_number
        self['rowPosition'] = row_position
        self['details'] = details
