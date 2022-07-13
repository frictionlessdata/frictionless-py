from __future__ import annotations
from .metadata import MetadataError


class ReportError(MetadataError):
    type = "report-error"
    title = "Report Error"
    description = "Provided report is not valid."
    template = "Report is not valid: {note}"


class ReportTaskError(ReportError):
    type = "report-task-error"
    title = "Report Task Error"
    description = "Provided report task is not valid."
    template = "Report task is not valid: {note}"
