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

        # Only forward basepath when explicitly provided
        basepath_opt: dict[str, Any] = {}
        if basepath is not None:
            basepath_opt["basepath"] = basepath

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
                    # PackageResource's datatype is fixed by its ClassVar
                    options.pop("datatype", None)
                    resource = resources.PackageResource(
                        data=data, basepath=package.basepath, **options
                    )
                    return cast(T, resource)

        # Path/data
        if source is not None:
            path = source
            if isinstance(source, str):
                path = helpers.join_basepath(source, basepath=basepath)

            md_type = options.get("datatype")
            if not md_type:
                md_type = Detector.detect_metadata_type(
                    path, format=options.get("format")
                )

            if md_type != "resource":
                options["path" if isinstance(source, str) else "data"] = source
                resource = cls(control=control, **basepath_opt, **options)  # type: ignore
                return cast(T, resource)

        # Descriptor
        if source is not None:
            options.pop("format", None)
            resource = cls.from_descriptor(  # type: ignore
                source, control=control, basepath=basepath, **options
            )
            return cast(T, resource)

        # Control
        if control is not None:
            dialect = options.pop("dialect", None)
            if dialect is None:
                dialect = control.to_dialect()
            elif control not in dialect.controls:
                dialect.add_control(control)
            options["dialect"] = dialect
            resource = cls(**basepath_opt, **options)  # type: ignore
            return cast(T, resource)

        # Routing: `datatype` is a hint for class selection only — strip it
        # before constructing so it isn't forwarded to __init__.
        if cls is platform.frictionless.Resource:
            explicit_datatype = options.pop("datatype", None)
            Router = type(
                "Router", (platform.frictionless.Resource,), {"_is_router": True}
            )
            resource = Router(**basepath_opt, **options)
            dt_match, _ = system.matches_datatype(resource)
            datatype = explicit_datatype or dt_match or "file"
            Class = system.select_resource_class(datatype=datatype)
            resource = Class(**basepath_opt, **options)
            return cast(T, resource)

        # Default
        options.pop("datatype", None)
        return cast(T, type.__call__(cls, **basepath_opt, **options))
