from ..error import Error


class DetectorError(Error):
    code = "detector-error"
    name = "Detector Error"
    template = "Detector is not valid: {note}"
    description = "Provided detector is not valid."
