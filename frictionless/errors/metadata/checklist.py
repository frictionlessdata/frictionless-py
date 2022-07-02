from .metadata import MetadataError


class ChecklistError(MetadataError):
    code = "checklist-error"
    name = "Checklist Error"
    template = "Checklist is not valid: {note}"
    description = "Provided checklist is not valid."


class CheckError(ChecklistError):
    code = "check-error"
    name = "Check Error"
    template = "Check is not valid: {note}"
    description = "Provided check is not valid"
