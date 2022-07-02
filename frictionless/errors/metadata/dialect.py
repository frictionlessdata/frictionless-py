from .metadata import MetadataError


class DialectError(MetadataError):
    code = "dialect-error"
    name = "Dialect Error"
    template = "Dialect is not valid: {note}"
    description = "Provided dialect is not valid."


class ControlError(DialectError):
    code = "control-error"
    name = "Control Error"
    template = "Control is not valid: {note}"
    description = "Provided control is not valid."
