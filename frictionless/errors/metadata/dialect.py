from __future__ import annotations
from .metadata import MetadataError


class DialectError(MetadataError):
    type = "dialect-error"
    titlte = "Dialect Error"
    description = "Provided dialect is not valid."
    template = "Dialect is not valid: {note}"


class ControlError(DialectError):
    type = "control-error"
    titlte = "Control Error"
    description = "Provided control is not valid."
    template = "Control is not valid: {note}"
