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

    @staticmethod
    def from_exception(exception):
        Error = SourceError
        details = str(exception)
        if isinstance(exception, tabulator.exceptions.IOError):
            Error = LoadingError
        if isinstance(exception, tabulator.exceptions.SourceError):
            Error = SourceError
        if isinstance(exception, tabulator.exceptions.SchemeError):
            Error = SchemeError
        if isinstance(exception, tabulator.exceptions.FormatError):
            Error = FormatError
        if isinstance(exception, tabulator.exceptions.EncodingError):
            Error = EncodingError
        if isinstance(exception, tableschema.exceptions.TableSchemaException):
            Error = SchemaError
        return Error(details=details)


# Table


class LoadingError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'loading-error'
    name = 'Loading Error'
    tags = ['table']
    message = 'The data source could not be successfully loaded: {details}'
    description = 'Data reading error because of IO error.'


class SourceError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'source-error'
    name = 'Source Error'
    tags = ['table']
    message = 'The data source has not supported or has inconsistent contents: {details}'
    description = 'Data reading error because of not supported or inconsistent contents.'


class SchemeError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'scheme-error'
    name = 'Scheme Error'
    tags = ['table']
    message = 'The data source is in an unknown scheme: {details}'
    description = 'Data reading error because of incorrect scheme.'


class FormatError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'format-error'
    name = 'Format Error'
    tags = ['table']
    message = 'The data source is in an unknown format: {details}'
    description = 'Data reading error because of incorrect format.'


class EncodingError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'encoding-error'
    name = 'Encoding Error'
    tags = ['table']
    message = 'The data source could not be successfully decoded: {details}'
    description = 'Data reading error because of an encoding problem.'


class SchemaError(Error):
    """
    # Arguments
        details (str)
    """

    code = 'schema-error'
    name = 'Schema Error'
    tags = ['table']
    message = 'Table Schema could not be used as it is invalid: {details}'
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
    tags = ['head', 'structure']
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
    tags = ['head', 'structure']
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
    tags = ['head', 'schema']
    message = 'There is an extra header in field {fieldName} at position {fieldPosition}'
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
    tags = ['head', 'schema']
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
    tags = ['head', 'schema']
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
    tags = ['body', 'structure']
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
    tags = ['body', 'structure']
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
    tags = ['body', 'structure']
    message = 'Row at position {rowPosition} has a missing cell in field {fieldName} at position {fieldPosition}'
    description = 'This row has less values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.'
