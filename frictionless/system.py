import os
import pkgutil
from collections import OrderedDict
from importlib import import_module
from .helpers import cached_property
from . import exceptions
from . import errors
from . import config


# NOTE: Consider plugins priority
# NOTE: Consider an ability to register plugins dynamically
class System:
    """System representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import system`

    This class provides an ability to make system Frictionless calls.
    It's available as `frictionless.system` singletone.

    """

    # Actions

    actions = [
        "create_check",
        "create_control",
        "create_dialect",
        "create_loader",
        "create_parser",
        "create_server",
        "create_storage",
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
        raise exceptions.FrictionlessException(errors.CheckError(note=note))

    def create_control(self, file, *, descriptor):
        """Create control

        Parameters:
            file (File): control file
            descriptor (dict): control descriptor

        Returns:
            Control: control
        """
        control = None
        name = file.scheme
        controls = import_module("frictionless.controls")
        for func in self.methods["create_control"].values():
            control = func(file, descriptor=descriptor)
            if control is not None:
                return control
        if name == "file":
            return controls.LocalControl(descriptor)
        elif name in config.REMOTE_SCHEMES:
            return controls.RemoteControl(descriptor)
        elif name == "stream":
            return controls.StreamControl(descriptor)
        elif name == "text":
            return controls.TextControl(descriptor)
        return controls.Control(descriptor)

    def create_dialect(self, file, *, descriptor):
        """Create dialect

        Parameters:
            file (File): dialect file
            descriptor (dict): dialect descriptor

        Returns:
            Dialect: dialect
        """
        dialect = None
        name = file.format
        dialects = import_module("frictionless.dialects")
        for func in self.methods["create_dialect"].values():
            dialect = func(file, descriptor=descriptor)
            if dialect is not None:
                return dialect
        if name == "csv":
            return dialects.CsvDialect(descriptor)
        elif name == "inline":
            return dialects.InlineDialect(descriptor)
        elif name in ["xlsx", "xls"]:
            return dialects.ExcelDialect(descriptor)
        elif name in ["json", "jsonl", "ndjson"]:
            return dialects.JsonDialect(descriptor)
        return dialects.Dialect(descriptor)

    def create_loader(self, file):
        """Create loader

        Parameters:
            file (File): loader file

        Returns:
            Loader: loader
        """
        loader = None
        name = file.scheme
        loaders = import_module("frictionless.loaders")
        for func in self.methods["create_loader"].values():
            loader = func(file)
            if loader is not None:
                return loader
        if name == "file":
            return loaders.LocalLoader(file)
        elif name in config.REMOTE_SCHEMES:
            return loaders.RemoteLoader(file)
        elif name == "stream":
            return loaders.StreamLoader(file)
        elif name == "text":
            return loaders.TextLoader(file)
        note = f'cannot create loader "{name}". Try installing "frictionless-{name}"'
        raise exceptions.FrictionlessException(errors.SchemeError(note=note))

    def create_parser(self, file):
        """Create parser

        Parameters:
            file (File): parser file

        Returns:
            Parser: parser
        """
        parser = None
        name = file.format
        parsers = import_module("frictionless.parsers")
        for func in self.methods["create_parser"].values():
            parser = func(file)
            if parser is not None:
                return parser
        if name == "csv":
            return parsers.CsvParser(file)
        elif name == "inline":
            return parsers.InlineParser(file)
        elif name == "xlsx":
            return parsers.XlsxParser(file)
        elif name == "xls":
            return parsers.XlsParser(file)
        elif name == "json":
            return parsers.JsonParser(file)
        elif name in ["jsonl", "ndjson"]:
            return parsers.JsonlParser(file)
        note = f'cannot create parser "{name}". Try installing "frictionless-{name}"'
        raise exceptions.FrictionlessException(errors.FormatError(note=note))

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
            raise exceptions.FrictionlessException(errors.Error(note=note))
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
            raise exceptions.FrictionlessException(errors.Error(note=note))
        return storage

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
        plugins = OrderedDict()
        for name, module in modules.items():
            Plugin = getattr(module, f"{name.capitalize()}Plugin", None)
            if Plugin:
                plugin = Plugin()
                plugins[name] = plugin
        return plugins


system = System()
