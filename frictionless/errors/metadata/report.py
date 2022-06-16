from .metadata import MetadataError


class ReportError(MetadataError):
    code = "report-error"
    name = "Report Error"
    template = "Report is not valid: {note}"
    description = "Provided report is not valid."
