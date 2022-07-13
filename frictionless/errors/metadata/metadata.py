from __future__ import annotations
from ...error import Error


class MetadataError(Error):
    type = "metadata-error"
    title = "Metadata Error"
    description = "There is a metadata error."
    template = "Metaata error: {note}"
