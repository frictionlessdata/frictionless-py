from typing import Any, Optional, cast
from ..metadata import Metaclass
from ..platform import platform
from ..dialect import Control
from ..system import system
from .. import helpers


class Factory(Metaclass):
    def __call__(
        cls,
        source: Optional[Any] = None,
        *params: Any,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        **options: Any
    ):
        assert not params
        source = helpers.normalize_source(source)

        # Adapter
        if source is not None or control is not None:
            adapter = system.create_adapter(source, control=control, basepath=basepath)
            if adapter:
                catalog = adapter.read_catalog()
                return catalog

        # Descriptor
        if source is not None:
            return platform.frictionless.Catalog.from_descriptor(
                source, basepath=basepath, **options  # type: ignore
            )

        # Default
        return cast(
            platform.frictionless.Catalog,
            type.__call__(cls, control=control, basepath=basepath, **options),
        )
