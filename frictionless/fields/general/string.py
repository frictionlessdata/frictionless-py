import base64
import rfc3986
import validators
from dataclasses import dataclass
from ...schema import Field
from ... import settings


@dataclass
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

        # Create reader
        def value_reader(cell):
            if not isinstance(cell, str):
                return None
            if self.format == "default":
                return cell
            elif self.format == "uri":
                uri = rfc3986.uri_reference(cell)
                try:
                    uri_validator.validate(uri)
                except rfc3986.exceptions.ValidationError:  # type: ignore
                    return None
            elif self.format == "email":
                if not validators.email(cell):  # type: ignore
                    return None
            elif self.format == "uuid":
                if not validators.uuid(cell):  # type: ignore
                    return None
            elif self.format == "binary":
                try:
                    base64.b64decode(cell)
                except Exception:
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

    # TODO: use search/settings
    metadata_profile = settings.SCHEMA_PROFILE["properties"]["fields"]["items"]["anyOf"][
        0
    ].copy()
    metadata_profile["properties"]["missingValues"] = {}


# Internal

uri_validator = rfc3986.validators.Validator().require_presence_of("scheme")  # type: ignore
