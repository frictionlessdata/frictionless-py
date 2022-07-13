from __future__ import annotations
from .metadata import MetadataError


class ChecklistError(MetadataError):
    name = "Checklist Error"
    type = "checklist-error"
    template = "Checklist is not valid: {note}"
    description = "Provided checklist is not valid."


class CheckError(ChecklistError):
    name = "Check Error"
    type = "check-error"
    template = "Check is not valid: {note}"
    description = "Provided check is not valid"
