from ..error import Error


class ResourceError(Error):
    code = "resource-error"
    name = "Resource Error"
    template = "The data resource has an error: {note}"
    description = "A validation cannot be processed."


class SourceError(ResourceError):
    code = "source-error"
    name = "Source Error"
    template = "The data source has not supported or has inconsistent contents: {note}"
    description = "Data reading error because of not supported or inconsistent contents."


class SchemeError(ResourceError):
    code = "scheme-error"
    name = "Scheme Error"
    template = "The data source could not be successfully loaded: {note}"
    description = "Data reading error because of incorrect scheme."


class FormatError(ResourceError):
    code = "format-error"
    name = "Format Error"
    template = "The data source could not be successfully parsed: {note}"
    description = "Data reading error because of incorrect format."


class EncodingError(ResourceError):
    code = "encoding-error"
    name = "Encoding Error"
    template = "The data source could not be successfully decoded: {note}"
    description = "Data reading error because of an encoding problem."


class HashingError(ResourceError):
    code = "hashing-error"
    name = "Hashing Error"
    template = "The data source could not be successfully hashed: {note}"
    description = "Data reading error because of a hashing problem."


class CompressionError(ResourceError):
    code = "compression-error"
    name = "Compression Error"
    template = "The data source could not be successfully decompressed: {note}"
    description = "Data reading error because of a decompression problem."
