from .metadata import Metadata


class Dialect(Metadata):
    pass


class CsvDialect(Dialect):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'properties': {
            'delimiter': {'type': 'string'},
            'lineTerminator': {'type': 'string'},
            'quoteChar': {'type': 'string'},
            'doubleQuote': {'type': 'boolean'},
            'escapeChar': {'type': 'string'},
            'nullSequence': {'type': 'string'},
            'skipInitialSpace': {'type': 'boolean'},
            'header': {'type': 'boolean'},
            'commentChar': {'type': 'string'},
            'caseSensitiveHeader': {'type': 'boolean'},
        },
    }

    # Expand

    def expand(self):
        self.setdetault('delimiter', ',')
        self.setdetault('lineTerminator', '\r\n')
        self.setdetault('quoteChar', '""')
        self.setdetault('doubleQuote', True)
        self.setdetault('skipInitialSpace', True)
        self.setdetault('header', True)
        self.setdetault('caseSensitiveHeader', False)


class ExcelDialect(Dialect):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'properties': {
            'sheet': {'type': ['number', 'string']},
            'fillMergedCells': {'type': 'boolean'},
            'preserveFormatting': {'type': 'boolean'},
            'adjustFloatingPointError': {'type': 'boolean'},
        },
    }

    # Expand

    def expand(self):
        self.setdetault('sheet', 1)
        self.setdetault('fillMergedCells', False)
        self.setdetault('preserveFormatting', False)
        self.setdetault('adjustFloatingPointError', False)


class JsonDialect(Dialect):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'properties': {
            'keyed': {'type': 'boolean'},
            'lined': {'type': 'boolean'},
            'property': {'type': 'string'},
        },
    }

    # Expand

    def expand(self):
        self.setdetault('keyed', False)
        self.setdetault('lined', False)
