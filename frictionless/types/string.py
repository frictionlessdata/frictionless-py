import re
import uuid
import base64
import rfc3986.exceptions
import rfc3986.validators
import rfc3986.uri
from ..type import Type


class StringType(Type):
    """String type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    supported_constraints = [
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
            uri = uri_from_string(cell)
            try:
                uri_validator.validate(uri)
            except rfc3986.exceptions.ValidationError:
                return None
        elif self.field.format == "email":
            if not re.match(email_pattern, cell):
                return None
        elif self.field.format == "uuid":
            try:
                uuid.UUID(cell, version=4)
            except Exception:
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

email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
uri_from_string = rfc3986.uri.URIReference.from_string
uri_validator = rfc3986.validators.Validator().require_presence_of("scheme")
