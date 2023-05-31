from typing import Any, Optional, Union, cast
from ..metadata import Metaclass
from ..platform import platform
from .. import types


class Factory(Metaclass):
    def __call__(
        cls,
        descriptor: Optional[Union[types.IDescriptor, str]] = None,
        *params: Any,
        **options: Any
    ):
        assert not params

        # Description
        if descriptor is not None:
            return platform.frictionless.Schema.from_descriptor(descriptor, **options)

        # Default
        return cast(
            platform.frictionless.Schema,
            type.__call__(cls, **options),
        )
