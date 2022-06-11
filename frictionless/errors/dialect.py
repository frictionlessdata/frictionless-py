from .resource import ResourceError


# TODO: merge them into DialectError


class ControlError(ResourceError):
    code = "control-error"
    name = "Control Error"
    template = "Control is not valid: {note}"
    description = "Provided control is not valid."


class DialectError(ResourceError):
    code = "dialect-error"
    name = "Dialect Error"
    template = "Dialect is not valid: {note}"
    description = "Provided dialect is not valid."


class LayoutError(ResourceError):
    code = "layout-error"
    name = "Layout Error"
    template = "Layout is not valid: {note}"
    description = "Provided layout is not valid."
