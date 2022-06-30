from .metadata import MetadataError


class ReportError(MetadataError):
    code = "report-error"
    name = "Report Error"
    template = "Report is not valid: {note}"
    description = "Provided report is not valid."


class ReportTaskError(ReportError):
    code = "report-task-error"
    name = "Report Task Error"
    template = "Report task is not valid: {note}"
    description = "Provided report task is not valid."
