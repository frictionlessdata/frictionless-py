"""base_field_descriptor.py provides the base Pydantic model for all field descriptors"""

from __future__ import annotations

from pydantic import BaseModel, Field as PydanticField, model_validator
from typing import Any, Dict, List, Optional
from typing_extensions import Self


class BaseFieldDescriptor(BaseModel):
    """Data model of a (unspecialised) field descriptor"""

    name: str
    """
    The field descriptor MUST contain a name property.
    """

    title: Optional[str] = None
    """
    A human readable label or title for the field
    """

    description: Optional[str] = None
    """
    A description for this field e.g. "The recipient of the funds"
    """

    missing_values: Optional[List[str]] = PydanticField(
        default=None, alias="missingValues"
    )
    """
    A list of field values to consider as null values
    """

    example: Optional[Any] = None
    """
    An example of a value for the field.
    """

    @model_validator(mode="before")
    @classmethod
    def compat(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        # Backward compatibility for field.format

        format_ = data.get("format")
        if format_:
            if format_.startswith("fmt:"):
                data["format"] = format_[4:]

        return data

    @model_validator(mode="after")
    def validate_example(self) -> Self:
        """Validate that the example value can be converted using read_value() if available"""
        if self.example is not None:
            if hasattr(self, "read_value"):
                read_value_method = getattr(self, "read_value")
                result = read_value_method(self.example)
                if result is None:
                    raise ValueError(
                        f'example value "{self.example}" for field "{self.name}" is not valid'
                    )

        return self

