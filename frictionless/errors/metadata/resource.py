from .metadata import MetadataError


class ResourceError(MetadataError):
    name = "Resource Error"
    type = "resource-error"
    template = "The data resource has an error: {note}"
    description = "A validation cannot be processed."


class SourceError(ResourceError):
    name = "Source Error"
    type = "source-error"
    template = "The data source has not supported or has inconsistent contents: {note}"
    description = "Data reading error because of not supported or inconsistent contents."


class SchemeError(ResourceError):
    name = "Scheme Error"
    type = "scheme-error"
    template = "The data source could not be successfully loaded: {note}"
    description = "Data reading error because of incorrect scheme."


class FormatError(ResourceError):
    name = "Format Error"
    type = "format-error"
    template = "The data source could not be successfully parsed: {note}"
    description = "Data reading error because of incorrect format."


class EncodingError(ResourceError):
    name = "Encoding Error"
    type = "encoding-error"
    template = "The data source could not be successfully decoded: {note}"
    description = "Data reading error because of an encoding problem."


class HashingError(ResourceError):
    name = "Hashing Error"
    type = "hashing-error"
    template = "The data source could not be successfully hashed: {note}"
    description = "Data reading error because of a hashing problem."


class CompressionError(ResourceError):
    name = "Compression Error"
    type = "compression-error"
    template = "The data source could not be successfully decompressed: {note}"
    description = "Data reading error because of a decompression problem."
