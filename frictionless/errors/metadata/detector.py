from __future__ import annotations
from .metadata import MetadataError


class DetectorError(MetadataError):
    name = "Detector Error"
    type = "detector-error"
    template = "Detector is not valid: {note}"
    description = "Provided detector is not valid."
