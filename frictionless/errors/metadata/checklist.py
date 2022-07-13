from __future__ import annotations
from .metadata import MetadataError


class ChecklistError(MetadataError):
    type = "checklist-error"
    title = "Checklist Error"
    description = "Provided checklist is not valid."
    template = "Checklist is not valid: {note}"


class CheckError(ChecklistError):
    type = "check-error"
    title = "Check Error"
    description = "Provided check is not valid"
    template = "Check is not valid: {note}"
