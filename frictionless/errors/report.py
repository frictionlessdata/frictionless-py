from ..error import Error


class ReportError(Error):
    code = "report-error"
    name = "Report Error"
    template = "Report is not valid: {note}"
    description = "Provided report is not valid."
