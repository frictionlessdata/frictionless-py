from __future__ import annotations

import os
import pkgutil
from collections import OrderedDict
from contextlib import contextmanager
from functools import cached_property
from importlib import import_module
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional, Type

from .. import errors, settings
from ..dialect import Control
from ..exception import FrictionlessException
from ..platform import platform

if TYPE_CHECKING:
    from .. import types
    from ..checklist import Check
    from ..error import Error
    from ..package import Package
    from ..pipeline import Step
    from ..resource import Resource
    from ..schema import Field
    from .adapter import Adapter
    from .loader import Loader
    from .parser import Parser
    from .plugin import Plugin


# NOTE:
# Shall we add plugin.identity/priority/etc as we do in Livemark?


class System:
    """System representation

    This class provides an ability to make system Frictionless calls.
    It's available as `frictionless.system` singletone.

    """

    supported_hooks: ClassVar[List[str]] = [
        "create_adapter",
        "create_loader",
        "create_parser",
        "detect_resource",
        # TODO: replace by detect_schema?
        "detect_field_candidates",
        "select_check_class",
        "select_control_class",
        "select_error_class",
        "select_field_class",
        "select_package_class",
        "select_resource_class",
        "select_step_class",
    ]

    trusted: bool = settings.DEFAULT_TRUSTED
    """
    A flag that indicates if resource, path or package is trusted.
    """

    onerror: types.IOnerror = settings.DEFAULT_ONERROR
    """
    Type of action to take on Error such as "warn", "raise" or "ignore".
    """

    standards: types.IStandards = settings.DEFAULT_STANDARDS
    """
    Setting this value user can use feature of the specific version.
    The default value is v2.
    """

    def __init__(self):
        self.__dynamic_plugins: OrderedDict[str, Plugin] = OrderedDict()
        self.__http_session = None

    @property
    def http_session(self):
        """Return a HTTP session

        This method will return a new session or the session
        from `system.use_http_session` context manager

        Returns:
            requests.Session: a HTTP session
        """
        if not self.__http_session:
            http_session = platform.requests.Session()
            http_session.headers.update(settings.DEFAULT_HTTP_HEADERS)
            self.__http_session = http_session
        return self.__http_session

    @cached_property
    def methods(self) -> Dict[str, Any]:
        methods: Dict[str, Any] = {}
        for action in self.supported_hooks:
            methods[action] = OrderedDict()
            for name, plugin in self.plugins.items():
                if action in vars(type(plugin)):
                    func = getattr(plugin, action, None)
                    methods[action][name] = func
        return methods

    @cached_property
    def plugins(self) -> OrderedDict[str, Plugin]:
        modules: OrderedDict[str, Any] = OrderedDict()
        for item in pkgutil.iter_modules():
            if item.name.startswith("frictionless_"):
                module = import_module(item.name)
                modules[item.name.replace("frictionless_", "")] = module
        for group in ["schemes", "formats", "portals"]:
            module = import_module(f"frictionless.{group}")
            if module.__file__:
                path = os.path.dirname(module.__file__)
                for _, name, _ in pkgutil.iter_modules([path]):
                    module = import_module(f"frictionless.{group}.{name}")
                    modules[name] = module
        plugins = OrderedDict(self.__dynamic_plugins)
        for name, module in modules.items():
            Plugin = getattr(module, f"{name.capitalize()}Plugin", None)
            if Plugin:
                plugin = Plugin()
                plugins[name] = plugin
        return plugins

    # Register/Deregister

    def register(self, name: str, plugin: Plugin):
        """Register a plugin

        Parameters:
            name (str): plugin name
            plugin (Plugin): plugin to register
        """
        self.__dynamic_plugins[name] = plugin
        if "methods" in self.__dict__:
            del self.__dict__["plugins"]
            del self.__dict__["methods"]

    def deregister(self, name: str):
        """Deregister a plugin

        Parameters:
            name (str): plugin name
        """
        self.__dynamic_plugins.pop(name, None)
        if "methods" in self.__dict__:
            del self.__dict__["plugins"]
            del self.__dict__["methods"]

    # Context

    @contextmanager
    def use_context(
        self,
        *,
        trusted: Optional[bool] = None,
        onerror: Optional[types.IOnerror] = None,
        standards: Optional[types.IStandards] = None,
        http_session: Optional[Any] = None,
    ):
        # Current
        current_trusted = self.trusted
        current_onerror = self.onerror
        current_standards = self.standards
        current_http_session = self.__http_session

        # Update
        if trusted is not None:
            self.trusted = trusted
        if onerror is not None:
            self.onerror = onerror
        if standards is not None:
            self.standards = standards
        if http_session is not None:
            self.__http_session = http_session
        yield self

        # Recover
        self.trusted = current_trusted
        self.onerror = current_onerror
        self.standards = current_standards
        self.__http_session = current_http_session

    # Hooks

    def create_adapter(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
    ) -> Optional[Adapter]:
        """Create adapter

        Parameters:
            resource (Resource): loader resource

        Returns:
            Loader: loader
        """
        adapter = None
        for func in self.methods["create_adapter"].values():
            adapter = func(
                source, control=control, packagify=packagify, basepath=basepath
            )
            if adapter is not None:
                return adapter

    def create_loader(self, resource: Resource) -> Loader:
        """Create loader

        Parameters:
            resource (Resource): loader resource

        Returns:
            Loader: loader
        """
        loader = None
        name = resource.scheme
        for func in self.methods["create_loader"].values():
            loader = func(resource)
            if loader is not None:
                return loader
        note = f'scheme "{name}" is not supported'
        raise FrictionlessException(errors.SchemeError(note=note))

    def create_parser(self, resource: Resource) -> Parser:
        """Create parser

        Parameters:
            resource (Resource): parser resource

        Returns:
            Parser: parser
        """
        parser = None
        name = resource.format
        for func in self.methods["create_parser"].values():
            parser = func(resource)
            if parser is not None:
                return parser
        note = f'format "{name}" is not supported'
        raise FrictionlessException(errors.FormatError(note=note))

    def detect_resource(self, resource: Resource) -> None:
        """Hook into resource detection

        Parameters:
            resource (Resource): resource

        """
        resource.detector.detect_resource(resource)
        for func in self.methods["detect_resource"].values():
            func(resource)
        resource.datatype = resource.datatype or "file"

    def detect_field_candidates(self) -> List[dict[str, Any]]:
        """Create candidates

        Returns:
            dict[]: an ordered by priority list of type descriptors for type detection
        """
        candidates = settings.DEFAULT_FIELD_CANDIDATES.copy()
        for func in self.methods["detect_field_candidates"].values():
            func(candidates)
        return candidates

    def select_check_class(self, type: Optional[str] = None) -> Type[Check]:
        if not type:
            return platform.frictionless.Check
        for func in self.methods["select_check_class"].values():
            Class = func(type)
            if Class is not None:
                return Class
        for Class in vars(platform.frictionless_checks).values():
            if getattr(Class, "type", None) == type:
                return Class
        note = f'check type "{type}" is not supported'
        raise FrictionlessException(errors.CheckError(note=note))

    def select_control_class(self, type: Optional[str] = None) -> Type[Control]:
        if not type:
            return platform.frictionless.Control
        for func in self.methods["select_control_class"].values():
            Class = func(type)
            if Class is not None:
                return Class
        note = f'control type "{type}" is not supported'
        raise FrictionlessException(errors.ControlError(note=note))

    def select_error_class(self, type: Optional[str] = None) -> Type[Error]:
        if not type:
            return platform.frictionless.Error
        for func in self.methods["select_error_class"].values():
            Class = func(type)
            if Class is not None:
                return Class
        for Class in vars(platform.frictionless_errors).values():
            if getattr(Class, "type", None) == type:
                return Class
        note = f'error type "{type}" is not supported'
        raise FrictionlessException(errors.Error(note=note))

    def select_field_class(self, type: Optional[str] = None) -> Type[Field]:
        if not type:
            return platform.frictionless.Field
        for func in self.methods["select_field_class"].values():
            Class = func(type)
            if Class is not None:
                return Class
        for Class in vars(platform.frictionless_fields).values():
            if getattr(Class, "type", None) == type:
                return Class
        note = f'field type "{type}" is not supported'
        raise FrictionlessException(errors.FieldError(note=note))

    def select_package_class(self, type: Optional[str] = None) -> Type[Package]:
        if not type:
            return platform.frictionless.Package
        for func in self.methods["select_package_class"].values():
            Class = func(type)
            if Class is not None:
                return Class
        note = f'package type "{type}" is not supported'
        raise FrictionlessException(errors.FieldError(note=note))

    def select_resource_class(
        self, type: Optional[str] = None, *, datatype: Optional[str] = None
    ) -> Type[Resource]:
        if not type and not datatype:
            return platform.frictionless.Resource
        for func in self.methods["select_resource_class"].values():
            Class = func(type, datatype=datatype)
            if Class is not None:
                return Class
        for Class in vars(platform.frictionless_resources).values():
            if type:
                if getattr(Class, "type", None) == type:
                    return Class
            if datatype:
                if getattr(Class, "datatype", None) == datatype:
                    return Class
        note = f'resource type "{type or datatype}" is not supported'
        raise FrictionlessException(errors.ResourceError(note=note))

    def select_step_class(self, type: Optional[str] = None) -> Type[Step]:
        if not type:
            return platform.frictionless.Step
        for func in self.methods["select_step_class"].values():
            Class = func(type)
            if Class is not None:
                return Class
        for Class in vars(platform.frictionless_steps).values():
            if getattr(Class, "type", None) == type:
                return Class
        note = f'step type "{type}" is not supported'
        raise FrictionlessException(errors.StepError(note=note))


system = System()
