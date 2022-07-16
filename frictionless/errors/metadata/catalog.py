from __future__ import annotations
from .metadata import MetadataError


class CatalogError(MetadataError):
    type = "catalog-error"
    title = "Catalog Error"
    description = "A validation cannot be processed."
    template = "The data catalog has an error: {note}"
