from __future__ import annotations
import os
import pkgutil
from collections import OrderedDict
from importlib import import_module
from contextlib import contextmanager
from typing import TYPE_CHECKING, List, Any, Dict
from .exception import FrictionlessException
from .helpers import cached_property
from .control import Control
from .file import File
from . import settings
from . import errors

if TYPE_CHECKING:
    from .check import Check
    from .error import Error
    from .field2 import Field2
    from .loader import Loader
    from .parser import Parser
    from .plugin import Plugin
    from .resource import Resource
    from .step import Step
    from .storage import Storage
    from .type import Type


# NOTE:
# On the next iteration we can improve the plugin system to provide prioritization
# Also, we might cosider having plugin.name although module based naming might be enough


# TODO: finish typing
class System:
    """System representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import system`

    This class provides an ability to make system Frictionless calls.
    It's available as `frictionless.system` singletone.

    """

    def __init__(self):
        self.__dynamic_plugins = OrderedDict()
        self.__http_session = None

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

    hooks = [
        "create_check",
        "create_control",
        "create_error",
        "create_field",
        "create_field_candidates",
        "create_file",
        "create_loader",
        "create_parser",
        "create_step",
        "create_storage",
        "create_type",
    ]

    def create_check(self, descriptor: dict) -> Check:
        """Create check

        Parameters:
            descriptor (dict): check descriptor

        Returns:
            Check: check
        """
        code = descriptor.get("code", "")
        for func in self.methods["create_check"].values():
            check = func(descriptor)
            if check is not None:
                return check
        for Class in vars(import_module("frictionless.checks")).values():
            if getattr(Class, "code", None) == code:
                return Class.from_descriptor(descriptor)
        note = f'check "{code}" is not supported. Try installing "frictionless-{code}"'
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

    def create_error(self, descriptor: dict) -> Error:
        """Create error

        Parameters:
            descriptor (dict): error descriptor

        Returns:
            Error: error
        """
        code = descriptor.get("code", "")
        for func in self.methods["create_error"].values():
            error = func(descriptor)
            if error is not None:
                return error
        for Class in vars(import_module("frictionless.errors")).values():
            if getattr(Class, "code", None) == code:
                return Class(descriptor)
        note = f'error "{code}" is not supported. Try installing "frictionless-{code}"'
        raise FrictionlessException(note)

    def create_field(self, descriptor: dict) -> Field2:
        """Create field

        Parameters:
            descriptor (dict): field descriptor

        Returns:
            Field: field
        """
        # TODO: move to a proper place
        descriptor.setdefault("type", "any")
        type = descriptor.get("type", "")
        for func in self.methods["create_field"].values():
            field = func(descriptor)
            if field is not None:
                return field
        for Class in vars(import_module("frictionless.fields")).values():
            if getattr(Class, "type", None) == type:
                return Class.from_descriptor(descriptor)
        note = f'field "{type}" is not supported. Try installing "frictionless-{type}"'
        raise FrictionlessException(errors.FieldError(note=note))

    def create_field_candidates(self) -> List[dict]:
        """Create candidates

        Returns:
            dict[]: an ordered by priority list of type descriptors for type detection
        """
        candidates = settings.DEFAULT_FIELD_CANDIDATES.copy()
        for func in self.methods["create_field_candidates"].values():
            func(candidates)
        return candidates

    def create_file(self, source: Any, **options) -> File:
        """Create file

        Parameters:
            source (any): file source
            options (dict): file options

        Returns:
            File: file
        """
        file = File(source, **options)
        for func in self.methods["create_file"].values():
            plugin_file = func(file)
            if plugin_file is not None:
                return plugin_file
        return file

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
        note = f'scheme "{name}" is not supported. Try installing "frictionless-{name}"'
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
        note = f'format "{name}" is not supported. Try installing "frictionless-{name}"'
        raise FrictionlessException(errors.FormatError(note=note))

    def create_step(self, descriptor: dict) -> Step:
        """Create step

        Parameters:
            descriptor (dict): step descriptor

        Returns:
            Step: step
        """
        code = descriptor.get("code", "")
        for func in self.methods["create_step"].values():
            step = func(descriptor)
            if step is not None:
                return step
        for Class in vars(import_module("frictionless.steps")).values():
            if getattr(Class, "code", None) == code:
                return Class.from_descriptor(descriptor)
        note = f'step "{code}" is not supported. Try installing "frictionless-{code}"'
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
        note = f'storage "{name}" is not supported. Try installing "frictionless-{name}"'
        raise FrictionlessException(note)

    def create_type(self, field: Field) -> Type:
        """Create type

        Parameters:
            field (Field): corresponding field

        Returns:
            Type: type
        """
        code = field.type
        for func in self.methods["create_type"].values():
            type = func(field)
            if type is not None:
                return type
        for Class in vars(import_module("frictionless.types")).values():
            if getattr(Class, "code", None) == code:
                return Class(field)
        note = f'type "{code}" is not supported. Try installing "frictionless-{code}"'
        raise FrictionlessException(errors.FieldError(note=note))

    # Requests

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

    # Methods

    @cached_property
    def methods(self) -> Dict[str, Any]:
        methods = {}
        for action in self.hooks:
            methods[action] = OrderedDict()
            for name, plugin in self.plugins.items():
                if action in vars(type(plugin)):
                    func = getattr(plugin, action, None)
                    methods[action][name] = func
        return methods

    # Plugins

    @cached_property
    def plugins(self) -> OrderedDict[str, Plugin]:
        modules = OrderedDict()
        for item in pkgutil.iter_modules():
            if item.name.startswith("frictionless_"):
                module = import_module(item.name)
                modules[item.name.replace("frictionless_", "")] = module
        module = import_module("frictionless.plugins")
        if module.__file__:
            for _, name, _ in pkgutil.iter_modules([os.path.dirname(module.__file__)]):
                module = import_module(f"frictionless.plugins.{name}")
                modules[name] = module
        plugins = OrderedDict(self.__dynamic_plugins)
        for name, module in modules.items():
            Plugin = getattr(module, f"{name.capitalize()}Plugin", None)
            if Plugin:
                plugin = Plugin()
                plugins[name] = plugin
        return plugins


system = System()
