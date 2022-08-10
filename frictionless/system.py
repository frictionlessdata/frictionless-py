from __future__ import annotations
import os
import pkgutil
from collections import OrderedDict
from importlib import import_module
from contextlib import contextmanager
from functools import cached_property
from typing import TYPE_CHECKING, Optional, List, Any, Dict, Type
from .exception import FrictionlessException
from .dialect import Control
from . import settings
from . import errors

if TYPE_CHECKING:
    from .interfaces import IStandardsVersion
    from .resource import Resource, Loader, Parser
    from .package import Manager, Storage
    from .plugin import Plugin
    from .checklist import Check
    from .error import Error
    from .schema import Field
    from .pipeline import Step


# NOTE:
# On the next iteration we can improve the plugin system to provide prioritization
# Also, we might cosider having plugin.name although module based naming might be enough


# TODO: finish typing
class System:
    """System representation

    This class provides an ability to make system Frictionless calls.
    It's available as `frictionless.system` singletone.

    """

    standards_version: IStandardsVersion = settings.DEFAULT_STANDARDS_VERSION
    supported_hooks = [
        "create_check",
        "create_control",
        "create_field_candidates",
        "create_loader",
        "create_manager",
        "create_parser",
        "create_step",
        "create_storage",
        "detect_resource",
        "select_Check",
        "select_Control",
        "select_Error",
        "select_Field",
        "select_Step",
    ]

    def __init__(self):
        self.__dynamic_plugins = OrderedDict()
        self.__http_session = None

    # Props

    @cached_property
    def methods(self) -> Dict[str, Any]:
        methods = {}
        for action in self.supported_hooks:
            methods[action] = OrderedDict()
            for name, plugin in self.plugins.items():
                if action in vars(type(plugin)):
                    func = getattr(plugin, action, None)
                    methods[action][name] = func
        return methods

    @cached_property
    def plugins(self) -> OrderedDict[str, Plugin]:
        modules = OrderedDict()
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

    def register(self, name, plugin):
        """Register a plugin

        Parameters:
            name (str): plugin name
            plugin (Plugin): plugin to register
        """
        self.__dynamic_plugins[name] = plugin
        if "methods" in self.__dict__:
            del self.__dict__["plugins"]
            del self.__dict__["methods"]

    def deregister(self, name):
        """Deregister a plugin

        Parameters:
            name (str): plugin name
        """
        self.__dynamic_plugins.pop(name, None)
        if "methods" in self.__dict__:
            del self.__dict__["plugins"]
            del self.__dict__["methods"]

    # Hooks

    def create_check(self, descriptor: dict) -> Check:
        """Create check

        Parameters:
            descriptor (dict): check descriptor

        Returns:
            Check: check
        """
        type = descriptor.get("type", "")
        for func in self.methods["create_check"].values():
            check = func(descriptor)
            if check is not None:
                return check
        for Class in vars(import_module("frictionless.checks")).values():
            if getattr(Class, "type", None) == type:
                return Class.from_descriptor(descriptor)
        note = f'check "{type}" is not supported'
        raise FrictionlessException(errors.CheckError(note=note))

    def create_control(self, descriptor: dict) -> Control:
        """Create control

        Parameters:
            descriptor (dict): control descriptor

        Returns:
            Control: control
        """
        control = None
        for func in self.methods["create_control"].values():
            control = func(descriptor)
            if control is not None:
                return control
        return Control.from_descriptor(descriptor)

    def create_field_candidates(self) -> List[dict]:
        """Create candidates

        Returns:
            dict[]: an ordered by priority list of type descriptors for type detection
        """
        candidates = settings.DEFAULT_FIELD_CANDIDATES.copy()
        for func in self.methods["create_field_candidates"].values():
            func(candidates)
        return candidates

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

    def create_manager(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
    ) -> Optional[Manager]:
        """Create manager

        Parameters:
            resource (Resource): loader resource

        Returns:
            Loader: loader
        """
        manager = None
        for func in self.methods["create_manager"].values():
            manager = func(source, control=control)
            if manager is not None:
                return manager

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

    def create_step(self, descriptor: dict) -> Step:
        """Create step

        Parameters:
            descriptor (dict): step descriptor

        Returns:
            Step: step
        """
        type = descriptor.get("type", "")
        for func in self.methods["create_step"].values():
            step = func(descriptor)
            if step is not None:
                return step
        for Class in vars(import_module("frictionless.steps")).values():
            if getattr(Class, "type", None) == type:
                return Class.from_descriptor(descriptor)
        note = f'step "{type}" is not supported'
        raise FrictionlessException(errors.StepError(note=note))

    def create_storage(self, name: str, source: Any, **options) -> Storage:
        """Create storage

        Parameters:
            name (str): storage name
            options (str): storage options

        Returns:
            Storage: storage
        """
        for func in self.methods["create_storage"].values():
            storage = func(name, source, **options)
            if storage is not None:
                return storage
        note = f'storage "{name}" is not supported'
        raise FrictionlessException(note)

    def detect_resource(self, resource: Resource) -> None:
        """Hook into resource detection

        Parameters:
            resource (Resource): resource

        """
        for func in self.methods["detect_resource"].values():
            func(resource)

    def select_Check(self, type: str) -> Type[Check]:
        for func in self.methods["select_Check"].values():
            Class = func(type)
            if Class is not None:
                return Class
        for Class in vars(import_module("frictionless.checks")).values():
            if getattr(Class, "type", None) == type:
                return Class
        note = f'check type "{type}" is not supported'
        raise FrictionlessException(errors.CheckError(note=note))

    def select_Control(self, type: str) -> Type[Control]:
        for func in self.methods["select_Control"].values():
            Class = func(type)
            if Class is not None:
                return Class
        for Class in vars(import_module("frictionless.formats")).values():
            if getattr(Class, "type", None) == type:
                return Class
        note = f'control type "{type}" is not supported'
        raise FrictionlessException(errors.ControlError(note=note))

    def select_Error(self, type: str) -> Type[Error]:
        for func in self.methods["select_Error"].values():
            Class = func(type)
            if Class is not None:
                return Class
        for Class in vars(import_module("frictionless.errors")).values():
            if getattr(Class, "type", None) == type:
                return Class
        note = f'error type "{type}" is not supported'
        raise FrictionlessException(errors.Error(note=note))

    def select_Field(self, type: str) -> Type[Field]:
        for func in self.methods["select_Field"].values():
            Class = func(type)
            if Class is not None:
                return Class
        for Class in vars(import_module("frictionless.fields")).values():
            if getattr(Class, "type", None) == type:
                return Class
        note = f'field type "{type}" is not supported'
        raise FrictionlessException(errors.FieldError(note=note))

    def select_Step(self, type: str) -> Type[Step]:
        for func in self.methods["select_Step"].values():
            Class = func(type)
            if Class is not None:
                return Class
        for Class in vars(import_module("frictionless.steps")).values():
            if getattr(Class, "type", None) == type:
                return Class
        note = f'step type "{type}" is not supported'
        raise FrictionlessException(errors.StepError(note=note))

    # Context

    def get_http_session(self):
        """Return a HTTP session

        This method will return a new session or the session
        from `system.use_http_session` context manager

        Returns:
            requests.Session: a HTTP session
        """
        if self.__http_session:
            return self.__http_session
        return self.plugins["remote"].create_http_session()  # type: ignore

    @contextmanager
    def use_http_session(self, http_session=None):
        """HTTP session context manager

        ```
        session = requests.Session(...)
        with system.use_http_session(session):
            # work with frictionless using a user defined HTTP session
            report = validate(...)
        ```

        Parameters:
            http_session? (requests.Session): a session; will create a new if omitted
        """
        if self.__http_session:
            note = f"There is already HTTP session in use: {self.__http_session}"
            raise FrictionlessException(note)
        self.__http_session = http_session or self.get_http_session()
        yield self.__http_session
        self.__http_session = None

    @contextmanager
    def use_standards_version(self, version: IStandardsVersion):
        current = self.standards_version
        self.standards_version = version
        yield version
        self.standards_version = current


system = System()
