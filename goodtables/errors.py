import tabulator
import tableschema


class Error(dict):
    def __init__(self, **context):
        self.update(context)
        self['code'] = self.code
        self['name'] = self.name
        self['tags'] = self.tags
        self['message'] = self.message.format(**context)
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
    """
    # Arguments
        details (str)
    """

    code = 'report-error'
    name = 'Report Error'
    tags = ['#report']
    message = 'The validation report has an error: {details}'
    description = 'A validation cannot be finished.'


# Task


class TaskError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'task-error'
    name = 'Task Error'
    tags = ['#task']
    message = 'The validation task has an error: {details}'
    description = 'A validation cannot be processed.'


# Package


class PackageError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'package-error'
    name = 'Package Error'
    tags = ['#package']
    message = 'The data package has an error: {details}'
    description = 'A validation cannot be processed.'


# Resource


class ResourceError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'resource-error'
    name = 'Resource Error'
    tags = ['#resource']
    message = 'The data resource has an error: {details}'
    description = 'A validation cannot be processed.'


# Table


class SourceError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'source-error'
    name = 'Source Error'
    tags = ['#table']
    message = 'The data source has not supported or has inconsistent contents: {details}'
    description = 'Data reading error because of not supported or inconsistent contents.'


class SchemeError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'scheme-error'
    name = 'Scheme Error'
    tags = ['#table']
    message = 'The data source could not be successfully loaded: {details}'
    description = 'Data reading error because of incorrect scheme.'


class FormatError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'format-error'
    name = 'Format Error'
    tags = ['#table']
    message = 'The data source could not be successfully parsed: {details}'
    description = 'Data reading error because of incorrect format.'


class EncodingError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'encoding-error'
    name = 'Encoding Error'
    tags = ['#table']
    message = 'The data source could not be successfully decoded: {details}'
    description = 'Data reading error because of an encoding problem.'


class CompressionError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'compression-error'
    name = 'Compression Error'
    tags = ['#table']
    message = 'The data source could not be successfully decompressed: {details}'
    description = 'Data reading error because of a decompression problem.'


class SizeError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'size-error'
    name = 'Size Error'
    tags = ['#table', '#integrity']
    message = 'The data source does not match the expected size in bytes: {details}'
    description = 'This error can happen if the data is corrupted.'


class HashError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'hash-error'
    name = 'Hash Error'
    tags = ['#table', '#integrity']
    message = 'The data source does not match the expected hash: {details}'
    description = 'This error can happen if the data is corrupted.'


class SchemaError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'schema-error'
    name = 'Schema Error'
    tags = ['#table', '#schema']
    message = 'The data source could not be successfully described by the invalid Table Schema: {details}'
    description = 'Provided schema is not valid.'


# Head


class BlankHeaderError(Error):
    """
    # Arguments
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
    """

    code = 'blank-header'
    name = 'Blank Header'
    tags = ['#head', '#structure']
    message = 'Header in field at position {fieldPosition} is blank'
    description = 'A column in the header row is missing a value. Headers should be provided and not be blank.'


class DuplicateHeaderError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
        details (str)
    """

    code = 'duplicate-header'
    name = 'Duplicate Header'
    tags = ['#head', '#structure']
    message = 'Header {cell} in field at position {fieldPosition} is duplicated to header in field(s): {details}'
    description = 'Two columns in the header row have the same value. Column names should be unique.'


class ExtraHeaderError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldPosition (int)
    """

    code = 'extra-header'
    name = 'Extra Header'
    tags = ['#head', '#schema']
    message = 'There is an extra header {cell} in field at position {fieldPosition}'
    description = 'The first row of the data source contains header that does not exist in the schema.'


class MissingHeaderError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
    """

    code = 'missing-header'
    name = 'Missing Header'
    tags = ['#head', '#schema']
    message = 'There is a missing header in field {fieldName} at position {fieldPosition}'
    description = 'Based on the schema there should be a header that is missing in the first row of the data source.'


class NonMatchingHeaderError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
    """

    code = 'non-matching-header'
    name = 'Non-matching Header'
    tags = ['#head', '#schema']
    message = 'Header {cell} in field {fieldName} at position {fieldPosition} does not match the field name in the schema'
    description = 'One of the data source headers does not match the field name defined in the schema.'


# Body


class BlankRowError(Error):
    """
    # Arguments
        rowNumber (int)
        rowPosition (int)
    """

    code = 'blank-row'
    name = 'Blank Row'
    tags = ['#body', '#structure']
    message = 'Row at position {rowPosition} is completely blank'
    description = 'This row is empty. A row should contain at least one value.'


class ExtraCellError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldPosition (int)
        rowNumber (int)
        rowPosition (int)
    """

    code = 'extra-cell'
    name = 'Extra Cell'
    tags = ['#body', '#structure']
    message = 'Row at position {rowPosition} has an extra value in field at position {fieldPosition}'
    description = 'This row has more values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.'


class MissingCellError(Error):
    """
    # Arguments
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
        rowNumber (int)
        rowPosition (int)
    """

    code = 'missing-cell'
    name = 'Missing Cell'
    tags = ['#body', '#structure']
    message = 'Row at position {rowPosition} has a missing cell in field {fieldName} at position {fieldPosition}'
    description = 'This row has less values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.'


class TypeError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
        rowNumber (int)
        rowPosition (int)
        details (str)
    """

    code = 'type-error'
    name = 'Missing Cell'
    tags = ['#body', '#schema']
    message = 'The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has incompatible type: {details}'
    description = 'The value does not match the schema type and format for this field.'


class RequiredConstraintError(Error):
    """
    # Arguments
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
        rowNumber (int)
        rowPosition (int)
    """

    code = 'required-constraint'
    name = 'Required Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'Field {fieldName} at position {fieldPosition} is a required field, but row at position {rowPosition} has no value'
    description = 'This field is a required field, but it contains no value.'


class MinLengthConstraintError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
        rowNumber (int)
        rowPosition (int)
        details (str)
    """

    code = 'min-length-constraint'
    name = 'Minimum Length Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at positin {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the minumum length constraint: {details}'
    description = 'A length of this field value should be greater or equal than schema constraint value.'


class MaxLengthConstraintError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
        rowNumber (int)
        rowPosition (int)
        details (str)
    """

    code = 'max-length-constraint'
    name = 'Maximum Length Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at positin {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the maximum length constraint: {details}'
    description = 'A length of this field value should be less or equal than schema constraint value.'


class MinimumConstraintError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
        rowNumber (int)
        rowPosition (int)
        details (str)
    """

    code = 'minimum-constraint'
    name = 'Minimum Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at positin {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the minimum constraint: {details}'
    description = 'This field value should be greater or equal than constraint value.'


class MaximumConstraintError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
        rowNumber (int)
        rowPosition (int)
        details (str)
    """

    code = 'maximum-constraint'
    name = 'Maximum Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at positin {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the maximum constraint: {details}'
    description = 'This field value should be less or equal than constraint value.'


class PatternConstraintError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
        rowNumber (int)
        rowPosition (int)
        details (str)
    """

    code = 'pattern-constraint'
    name = 'Pattern Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at positin {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the pattern constraint: {details}'
    description = 'This field value should conform to constraint pattern.'


class EnumConstraintError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
        rowNumber (int)
        rowPosition (int)
        details (str)
    """

    code = 'enum-constraint'
    name = 'Enumerable Constraint'
    tags = ['#body', '#schema', '#constraint']
    message = 'The cell {cell} in row at positin {rowPosition} and field {fieldName} at position {fieldPosition} does not conform to the given enumeration: {details}'
    description = 'This field value should be equal to one of the values in the enumeration constraint.'


class UniqueConstraintError(Error):
    """
    # Arguments
        cell (str)
        cells (str[])
        fieldName (str)
        fieldNumber (int)
        fieldPosition (int)
        rowNumber (int)
        rowPosition (int)
        details (str)
    """

    code = 'unique-constraint'
    name = 'Unique Constraint'
    tags = ['#body', '#schema', '#constraint', '#integrity']
    message = 'Row at positi {rowPosition} has unique constraint violation in field {fieldName} at position {fieldPosition}: {details}'
    description = 'This field is a unique field but it contains a value that has been used in another row.'


class PrimaryKeyError(Error):
    """
    # Arguments
        cells (str[])
        rowNumber (int)
        rowPosition (int)
        details (str)
    """

    code = 'primary-key-error'
    name = 'Primary Key Error'
    tags = ['#body', '#schema', '#integrity']
    message = 'The row at position {rowPosition} does not conform to the primary key constraint: {details}'
    description = 'Values in the primary key fields should be unique for every row'


class ForeignKeyError(Error):
    """
    # Arguments
        cells (str[])
        rowNumber (int)
        rowPosition (int)
        details (str)
    """

    code = 'foreign-key-error'
    name = 'Foreign Key Error'
    tags = ['#body', '#schema', '#integrity']
    message = 'The row at position {rowPosition} does not conform to the foreign key constraint: {details}'
    description = 'Values in the foreign key fields should exist in the reference table'
