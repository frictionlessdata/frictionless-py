from .metadata import MetadataError


class DialectError(MetadataError):
    name = "Dialect Error"
    type = "dialect-error"
    template = "Dialect is not valid: {note}"
    description = "Provided dialect is not valid."


class ControlError(DialectError):
    name = "Control Error"
    type = "control-error"
    template = "Control is not valid: {note}"
    description = "Provided control is not valid."
