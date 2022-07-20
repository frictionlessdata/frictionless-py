from __future__ import annotations
from ...error import Error


class MetadataError(Error):
    type = "metadata-error"
    title = "Metadata Error"
    description = "There is a metadata error."
    template = "Metadata error: {note}"


class StatsError(MetadataError):
    type = "stats-error"
    title = "Stats Error"
    description = "Stats object has an error."
    template = "Stats object has an error: {note}"
