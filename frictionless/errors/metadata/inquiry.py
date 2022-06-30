from .metadata import MetadataError


class InquiryError(MetadataError):
    code = "inquiry-error"
    name = "Inquiry Error"
    template = "Inquiry is not valid: {note}"
    description = "Provided inquiry is not valid."


class InquiryTaskError(MetadataError):
    code = "inquiry-task-error"
    name = "Inquiry Task Error"
    template = "Inquiry task is not valid: {note}"
    description = "Provided inquiry task is not valid."
