from .metadata import MetadataError


class DetectorError(MetadataError):
    code = "detector-error"
    name = "Detector Error"
    template = "Detector is not valid: {note}"
    description = "Provided detector is not valid."
