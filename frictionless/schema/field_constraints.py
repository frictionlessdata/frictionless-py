"""field_constraints.py provide pydantic Models for constraints"""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

import pydantic

T = TypeVar("T")


class BaseConstraints(pydantic.BaseModel, Generic[T]):
    required: Optional[bool] = None
    unique: Optional[bool] = None
    enum: Optional[List[Union[str, T]]] = None


class CollectionConstraints(BaseConstraints[str]):
    minLength: Optional[int] = None
    maxLength: Optional[int] = None


class JSONConstraints(CollectionConstraints):
    jsonSchema: Optional[Dict[str, Any]] = None


class StringConstraints(CollectionConstraints):
    pattern: Optional[str] = None


class ValueConstraints(BaseConstraints[T], Generic[T]):
    minimum: Optional[Union[str, T]] = None
    maximum: Optional[Union[str, T]] = None
    exclusiveMinimum: Optional[Union[str, T]] = None
    exclusiveMaximum: Optional[Union[str, T]] = None
