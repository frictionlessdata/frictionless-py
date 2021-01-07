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


# TODO: Add plugin.name?
# TODO: Rework system.register
# TODO: Consider plugins priority
# TODO: Use lists instead of ordered dicts?
# TODO: Implement hard errors/memory limit setting
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
        "create_file",
        "create_loader",
        "create_parser",
        "create_pipeline",
        "create_server",
        "create_storage",
        "create_type",
    ]

    def create_check(self, name, *, descriptor=None):
        """Create checks

        Parameters:
            name (str): check name
            descriptor (dict): check descriptor

        Returns:
            Check: check
        """
        check = None
        checks = import_module("frictionless.checks")
        for func in self.methods["create_check"].values():
            check = func(name, descriptor=descriptor)
            if check is not None:
                return check
        if name == "baseline":
            return checks.BaselineCheck(descriptor)
        elif name == "checksum":
            return checks.ChecksumCheck(descriptor)
        elif name == "duplicate-row":
            return checks.DuplicateRowCheck(descriptor)
        elif name == "deviated-value":
            return checks.DeviatedValueCheck(descriptor)
        elif name == "truncated-value":
            return checks.TruncatedValueCheck(descriptor)
        elif name == "blacklisted-value":
            return checks.BlacklistedValueCheck(descriptor)
        elif name == "sequential-value":
            return checks.SequentialValueCheck(descriptor)
        elif name == "row-constraint":
            return checks.RowConstraintCheck(descriptor)
        note = f'cannot create check "{name}". Try installing "frictionless-{name}"'
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

    def create_pipeline(self, descriptor):
        """Create parser

        Parameters:
            descriptor (str|dict): pipeline descriptor

        Returns:
            Pipeline: pipeline
        """
        Metadata = import_module("frictionless.metadata").Metadata
        Pipeline = import_module("frictionless.pipeline").Pipeline
        type = Metadata(descriptor).get("type", "resource")
        for func in self.methods["create_pipeline"].values():
            pipeline = func(type, descriptor=descriptor)
            if pipeline is not None:
                return pipeline
        if type in ["resource", "package"]:
            return Pipeline(descriptor)
        note = f'cannot create pipeline "{type}". Try installing "frictionless-{type}"'
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
                break
        if server is None:
            note = f'cannot create server "{name}". Try installing "frictionless-{name}"'
            raise FrictionlessException(errors.Error(note=note))
        return server

    def create_storage(self, name, **options):
        """Create storage

        Parameters:
            name (str): storage name
            options (str): storage options

        Returns:
            Storage: storage
        """
        storage = None
        for func in self.methods["create_storage"].values():
            storage = func(name, **options)
            if storage is not None:
                break
        if storage is None:
            note = f'cannot create storage "{name}". Try installing "frictionless-{name}"'
            raise FrictionlessException(errors.Error(note=note))
        return storage

    def create_type(self, field):
        """Create checks

        Parameters:
            field (Field): corresponding field

        Returns:
            Type: type
        """
        name = field.type
        types = import_module("frictionless.types")
        for func in self.methods["create_type"].values():
            type = func(field)
            if type is not None:
                return type
        Class = getattr(types, f"{name.capitalize()}Type", getattr(types, "AnyType"))
        # TODO: review
        #  if Class is None:
        #  note = f'cannot create type "{name}". Try installing "frictionless-{name}"'
        #  raise FrictionlessException(errors.FieldError(note=note))
        return Class(field)

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
