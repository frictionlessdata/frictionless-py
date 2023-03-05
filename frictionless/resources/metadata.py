from __future__ import annotations
from typing import TYPE_CHECKING, Union
from .json import JsonResource

if TYPE_CHECKING:
    from ..interfaces import IDescriptor


class MetadataResource(JsonResource):
    @property
    def descriptor(self) -> Union[IDescriptor, str]:
        descriptor = self.data if self.data is not None else self.path
        assert isinstance(descriptor, (str, dict))
        return descriptor
