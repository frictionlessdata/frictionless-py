from __future__ import annotations
from .metadata import MetadataError


class ResourceError(MetadataError):
    type = "resource-error"
    title = "Resource Error"
    description = "A validation cannot be processed."
    template = "The data resource has an error: {note}"


class SourceError(ResourceError):
    type = "source-error"
    title = "Source Error"
    description = "Data reading error because of not supported or inconsistent contents."
    template = "The data source has not supported or has inconsistent contents: {note}"


class SchemeError(ResourceError):
    type = "scheme-error"
    title = "Scheme Error"
    description = "Data reading error because of incorrect scheme."
    template = "The data source could not be successfully loaded: {note}"


class FormatError(ResourceError):
    type = "format-error"
    title = "Format Error"
    description = "Data reading error because of incorrect format."
    template = "The data source could not be successfully parsed: {note}"


class EncodingError(ResourceError):
    type = "encoding-error"
    title = "Encoding Error"
    description = "Data reading error because of an encoding problem."
    template = "The data source could not be successfully decoded: {note}"


class CompressionError(ResourceError):
    type = "compression-error"
    title = "Compression Error"
    description = "Data reading error because of a decompression problem."
    template = "The data source could not be successfully decompressed: {note}"
