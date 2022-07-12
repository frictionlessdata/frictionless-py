from .metadata import MetadataError


class ReportError(MetadataError):
    name = "Report Error"
    type = "report-error"
    template = "Report is not valid: {note}"
    description = "Provided report is not valid."


class ReportTaskError(ReportError):
    name = "Report Task Error"
    type = "report-task-error"
    template = "Report task is not valid: {note}"
    description = "Provided report task is not valid."
