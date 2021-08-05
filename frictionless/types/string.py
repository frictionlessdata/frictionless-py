import base64
import rfc3986
import validators
from ..type import Type


class StringType(Type):
    """String type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    code = "string"
    builtin = True
    constraints = [
        "required",
        "minLength",
        "maxLength",
        "pattern",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        if not isinstance(cell, str):
            return None
        if self.field.format == "default":
            return cell
        elif self.field.format == "uri":
            uri = rfc3986.uri_reference(cell)
            try:
                uri_validator.validate(uri)
            except rfc3986.exceptions.ValidationError:
                return None
        elif self.field.format == "email":
            if not validators.email(cell):
                return None
        elif self.field.format == "uuid":
            if not validators.uuid(cell):
                return None
        elif self.field.format == "binary":
            try:
                base64.b64decode(cell)
            except Exception:
                return None
        return cell

    # Write

    def write_cell(self, cell):
        return cell


# Internal

uri_validator = rfc3986.validators.Validator().require_presence_of("scheme")
