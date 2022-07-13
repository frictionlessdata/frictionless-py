from __future__ import annotations
from .metadata import MetadataError


class DetectorError(MetadataError):
    type = "detector-error"
    title = "Detector Error"
    description = "Provided detector is not valid."
    template = "Detector is not valid: {note}"
