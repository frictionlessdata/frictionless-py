from .metadata import MetadataError


# TODO: merge them into DialectError


class ControlError(MetadataError):
    code = "control-error"
    name = "Control Error"
    template = "Control is not valid: {note}"
    description = "Provided control is not valid."


class DialectError(MetadataError):
    code = "dialect-error"
    name = "Dialect Error"
    template = "Dialect is not valid: {note}"
    description = "Provided dialect is not valid."


class LayoutError(MetadataError):
    code = "layout-error"
    name = "Layout Error"
    template = "Layout is not valid: {note}"
    description = "Provided layout is not valid."
