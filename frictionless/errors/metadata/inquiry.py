from __future__ import annotations
from .metadata import MetadataError


class InquiryError(MetadataError):
    type = "inquiry-error"
    title = "Inquiry Error"
    description = "Provided inquiry is not valid."
    template = "Inquiry is not valid: {note}"


class InquiryTaskError(MetadataError):
    type = "inquiry-task-error"
    title = "Inquiry Task Error"
    description = "Provided inquiry task is not valid."
    template = "Inquiry task is not valid: {note}"
