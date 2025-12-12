import base64
from typing import Any, Literal, Optional, Union, List

from pydantic import Field as PydanticField, BaseModel
from ..platform import platform
from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import StringConstraints

class CategoryDict(BaseModel):
    """Category dictionary for field categories."""
    value: str
    label: Optional[str] = None


ICategories = Union[
    List[str],
    List[CategoryDict],
]
"""Categories type used by IntegerFieldDescriptor and StringFieldDescriptor"""
class StringFieldDescriptor(BaseFieldDescriptor):
    """The field contains strings, that is, sequences of characters."""

    type: Literal["string"] = "string"
    format: Optional[Literal["default", "binary", "email", "uri", "uuid", "wkt"]] = None
    constraints: StringConstraints = PydanticField(default_factory=StringConstraints)

    categories: Optional[ICategories] = None
    """
    Property to restrict the field to a finite set of possible values
    """

    categoriesOrdered: Optional[bool] = PydanticField(default=None, alias="categoriesOrdered")
    """
    When categoriesOrdered is true, implementations SHOULD regard the order of
    appearance of the values in the categories property as their natural order.
    """

    def read_value(self, cell: Any) -> Optional[str]:
        format_value = self.format or "default"

        # Uri
        if format_value == "uri":
            if not isinstance(cell, str):
                return None
            uri_validator = platform.rfc3986.validators.Validator()  # type: ignore
            uri_validator.require_presence_of("scheme")  # type: ignore
            uri = platform.rfc3986.uri_reference(cell)  # type: ignore
            try:
                uri_validator.validate(uri)  # type: ignore
            except platform.rfc3986.exceptions.ValidationError:  # type: ignore
                return None
            return cell

        # Email
        elif format_value == "email":
            if not isinstance(cell, str):
                return None
            result = platform.validators.email(cell)  # type: ignore
            if result is True:
                return cell
            return None

        # Uuid
        elif format_value == "uuid":
            if not isinstance(cell, str):
                return None
            if not platform.validators.uuid(cell):  # type: ignore
                return None
            return cell

        # Binary
        elif format_value == "binary":
            if not isinstance(cell, str):
                return None
            try:
                base64.b64decode(cell)
            except Exception:
                return None
            return cell

        # WKT
        elif format_value == "wkt":
            parser = platform.wkt.Parser()
            if not isinstance(cell, str):
                return None
            try:
                parser.parse(cell)
            except Exception:
                return None
            return cell

        # Default
        else:
            if not isinstance(cell, str):
                return None
            return cell

    def write_value(self, cell: Any) -> Optional[str]:
        if cell is None:
            return None
        return str(cell)

