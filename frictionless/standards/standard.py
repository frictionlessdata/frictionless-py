from __future__ import annotations
import attrs
import pydantic
from typing import Type, TypedDict


@attrs.define(kw_only=True)
class Standard:
    definition: Type[TypedDict]

    def to_jsonschema(self):
        return pydantic.create_model_from_typeddict(self.definition).schema()  # type: ignore
