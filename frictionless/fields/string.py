from __future__ import annotations
import attrs
import base64
from ..schema import Field
from ..platform import platform


@attrs.define(kw_only=True)
class StringField(Field):
    type = "string"
    builtin = True
    supported_constraints = [
        "required",
        "minLength",
        "maxLength",
        "pattern",
        "enum",
    ]

    # Read

    def create_value_reader(self):

        # Uri
        if self.format == "uri":

            def value_reader(cell):
                if not isinstance(cell, str):
                    return None
                uri_validator = platform.rfc3986.validators.Validator()  # type: ignore
                uri_validator.require_presence_of("scheme")
                uri = platform.rfc3986.uri_reference(cell)
                try:
                    uri_validator.validate(uri)  # type: ignore
                except platform.rfc3986.exceptions.ValidationError:  # type: ignore
                    return None
                return cell

        # Email
        elif self.format == "email":

            def value_reader(cell):
                if not isinstance(cell, str):
                    return None
                if not platform.validators.email(cell):  # type: ignore
                    return None
                return cell

        # Uuid
        elif self.format == "uuid":

            def value_reader(cell):
                if not isinstance(cell, str):
                    return None
                if not platform.validators.uuid(cell):  # type: ignore
                    return None
                return cell

        # Binary
        elif self.format == "binary":

            def value_reader(cell):
                if not isinstance(cell, str):
                    return None
                try:
                    base64.b64decode(cell)
                except Exception:
                    return None
                return cell

        # WKT
        elif self.format == "wkt":
            parser = platform.wkt.WktParser()

            def value_reader(cell):
                if not isinstance(cell, str):
                    return None
                try:
                    parser.parse(cell, rule_name="wkt_representation")
                except Exception:
                    return None
                return cell

        # Default
        else:

            def value_reader(cell):
                if not isinstance(cell, str):
                    return None

                return cell

        return value_reader

    # Write

    def create_value_writer(self):

        # Create writer
        def value_writer(cell):
            return str(cell)

        return value_writer

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "format": {
                "type": "string",
                "enum": ["default", "email", "uri", "binary", "uuid", "wkt"],
            },
        }
    }


# Internal
