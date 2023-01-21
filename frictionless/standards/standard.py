from __future__ import annotations
import attrs
import pydantic
from typing import Type, TypedDict


@attrs.define(kw_only=True)
class Standard:
    definition: Type[TypedDict]

    # TODO: before pydantic@2 we have naming conflicts due:
    # https://github.com/pydantic/pydantic/issues/1001
    def to_jsonschema(self):
        return pydantic.create_model_from_typeddict(self.definition).schema()  # type: ignore
