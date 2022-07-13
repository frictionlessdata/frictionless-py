from __future__ import annotations
from .metadata import MetadataError


class PackageError(MetadataError):
    type = "package-error"
    title = "Package Error"
    description = "A validation cannot be processed."
    template = "The data package has an error: {note}"
