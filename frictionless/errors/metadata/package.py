from __future__ import annotations
from .metadata import MetadataError


class PackageError(MetadataError):
    name = "Package Error"
    type = "package-error"
    template = "The data package has an error: {note}"
    description = "A validation cannot be processed."
