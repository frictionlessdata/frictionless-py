import os
import pkgutil
from collections import OrderedDict
from importlib import import_module
from .exception import FrictionlessException
from .helpers import cached_property
from .control import Control
from .dialect import Dialect
from .file import File
from . import errors


# NOTE:
# On the next iteration we can improve the plugin system to provide prioritization
# Also, we might cosider having plugin.name although module based naming might be enough


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

    # Actions

    actions = [
        "create_check",
        "create_control",
        "create_dialect",
        "create_error",
        "create_file",
        "create_loader",
        "create_parser",
        "create_server",
        "create_step",
        "create_storage",
        "create_type",
    ]

    def create_check(self, descriptor):
        """Create checks

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
                return Class(descriptor)
        note = f'cannot create check "{code}". Try installing "frictionless-{code}"'
        raise FrictionlessException(errors.CheckError(note=note))

    def create_control(self, resource, *, descriptor):
        """Create control

        Parameters:
            resource (Resource): control resource
            descriptor (dict): control descriptor

        Returns:
            Control: control
        """
        control = None
        for func in self.methods["create_control"].values():
            control = func(resource, descriptor=descriptor)
            if control is not None:
                return control
        return Control(descriptor)

    def create_dialect(self, resource, *, descriptor):
        """Create dialect

        Parameters:
            resource (Resource): dialect resource
            descriptor (dict): dialect descriptor

        Returns:
            Dialect: dialect
        """
        dialect = None
        for func in self.methods["create_dialect"].values():
            dialect = func(resource, descriptor=descriptor)
            if dialect is not None:
                return dialect
        return Dialect(descriptor)

    def create_error(self, descriptor):
        """Create errors

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
        note = f'cannot create error "{code}". Try installing "frictionless-{code}"'
        raise FrictionlessException(errors.Error(note=note))

    def create_file(self, source, **options):
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

    def create_loader(self, resource):
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
        note = f'cannot create loader "{name}". Try installing "frictionless-{name}"'
        raise FrictionlessException(errors.SchemeError(note=note))

    def create_parser(self, resource):
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
        note = f'cannot create parser "{name}". Try installing "frictionless-{name}"'
        raise FrictionlessException(errors.FormatError(note=note))

    def create_server(self, name, **options):
        """Create server

        Parameters:
            name (str): server name
            options (str): server options

        Returns:
            Server: server
        """
        server = None
        for func in self.methods["create_server"].values():
            server = func(name, **options)
            if server is not None:
                return server
        note = f'cannot create server "{name}". Try installing "frictionless-{name}"'
        raise FrictionlessException(errors.GeneralError(note=note))

    def create_step(self, descriptor):
        """Create steps

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
                return Class(descriptor)
        note = f'cannot create check "{code}". Try installing "frictionless-{code}"'
        raise FrictionlessException(errors.StepError(note=note))

    def create_storage(self, name, source, **options):
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
        note = f'cannot create storage "{name}". Try installing "frictionless-{name}"'
        raise FrictionlessException(errors.GeneralError(note=note))

    def create_type(self, field):
        """Create checks

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
        note = f'cannot create type "{code}". Try installing "frictionless-{code}"'
        raise FrictionlessException(errors.FieldError(note=note))

    # Methods

    @cached_property
    def methods(self):
        methods = {}
        for action in self.actions:
            methods[action] = OrderedDict()
            for name, plugin in self.plugins.items():
                if action in vars(type(plugin)):
                    func = getattr(plugin, action, None)
                    methods[action][name] = func
        return methods

    # Plugins

    @cached_property
    def plugins(self):
        modules = OrderedDict()
        for item in pkgutil.iter_modules():
            if item.name.startswith("frictionless_"):
                module = import_module(item.name)
                modules[item.name] = module
        module = import_module("frictionless.plugins")
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
