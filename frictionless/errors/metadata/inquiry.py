from .metadata import MetadataError


class InquiryError(MetadataError):
    name = "Inquiry Error"
    type = "inquiry-error"
    template = "Inquiry is not valid: {note}"
    description = "Provided inquiry is not valid."


class InquiryTaskError(MetadataError):
    name = "Inquiry Task Error"
    type = "inquiry-task-error"
    template = "Inquiry task is not valid: {note}"
    description = "Provided inquiry task is not valid."
