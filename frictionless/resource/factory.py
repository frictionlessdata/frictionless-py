from typing import Any, Generic, Optional, TypeVar, cast

from .. import helpers
from ..detector import Detector
from ..dialect import Control
from ..platform import platform
from ..system import system

T = TypeVar("T")


class Factory(type, Generic[T]):
    def __call__(
        cls,
        source: Optional[Any] = None,
        *params: Any,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
        **options: Any,
    ):
        assert not params
        source = helpers.normalize_source(source)
        resources = platform.frictionless_resources

        # Adapter
        if source is not None:
            adapter = system.create_adapter(
                source,
                control=control,
                basepath=basepath,
                packagify=packagify,
            )
            if adapter:
                package = adapter.read_package()
                if package:
                    data = package.to_descriptor()
                    resource = resources.PackageResource(
                        data=data, basepath=package.basepath, **options
                    )
                    return cast(T, resource)

        # Path/data
        if source is not None:
            path = source
            if isinstance(source, str):
                path = helpers.join_basepath(source, basepath=basepath)
            md_type = Detector.detect_metadata_type(path, format=options.get("format"))
            if md_type != "resource":
                options["path" if isinstance(source, str) else "data"] = source
                resource = cls(control=control, basepath=basepath, **options)  # type: ignore
                return cast(T, resource)

        # Descriptor
        if source is not None:
            options.pop("format", None)
            resource = cls.from_descriptor(source, control=control, basepath=basepath, **options)  # type: ignore
            return cast(T, resource)

        # Control
        if control is not None:
            dialect = options.pop("dialect", None)
            if dialect is None:
                dialect = control.to_dialect()
            elif control not in dialect.controls:
                dialect.add_control(control)
            options["dialect"] = dialect
            resource = cls(basepath=basepath, **options)  # type: ignore
            return cast(T, resource)

        # Routing
        if cls is platform.frictionless.Resource:
            Router = type("Router", (platform.frictionless.Resource,), {})
            resource = Router(basepath=basepath, **options)
            Class = system.select_resource_class(datatype=resource.datatype)
            resource = Class(basepath=basepath, **options)
            return cast(T, resource)

        # Default
        return cast(T, type.__call__(cls, basepath=basepath, **options))
