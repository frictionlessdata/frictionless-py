from typing import Any, Optional, Union, cast

from .. import types
from ..platform import platform


class Factory(type):
    def __call__(
        cls,
        descriptor: Optional[Union[types.IDescriptor, str]] = None,
        *params: Any,
        **options: Any,
    ):
        assert not params

        # Descriptor
        if descriptor is not None:
            return cast(
                platform.frictionless.Schema,
                cls.from_descriptor(descriptor, **options),  # type: ignore
            )

        # Default
        return cast(
            platform.frictionless.Schema,
            type.__call__(cls, **options),
        )
