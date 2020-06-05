import importlib
from . import exceptions


class System:
    def __init__(self):
        self.__plugins = {}

    # Checks

    def create_check(self, name, *, descriptor=None):
        if isinstance(name, type):
            return name(descriptor)
        plugin_name, *rest = name.split('/', 1)
        plugin = self.load_plugin(plugin_name)
        check = plugin.create_check(name, descriptor=descriptor)
        if not check:
            message = f'Plugin "{plugin_name}" does not support check "{name}"'
            raise exceptions.GoodtablesException(message)
        return check

    # Servers

    def create_server(self, name):
        if isinstance(name, type):
            return name()
        plugin_name, *rest = name.split('/', 1)
        plugin = self.load_plugin(plugin_name)
        server = plugin.create_server(name)
        if not server:
            message = f'Plugin "server" does not support server "{name}"'
            raise exceptions.GoodtablesException(message)
        return server

    # Plugins

    def load_plugin(self, name):
        if name not in self.__plugins:
            module = None
            internal = f'goodtables.plugins.{name}'
            external = f'goodtables-{name}'
            for module_name in [internal, external]:
                try:
                    module = importlib.import_module(module_name)
                    break
                except ImportError as exception:
                    # Plugin is available but its dependencies are not
                    if module_name == getattr(exception, 'name', None):
                        command = f'pip install goodtables[{name}]'
                        message = f'Plugin "{name}" is not installed. Run: "{command}"'
                        raise exceptions.GoodtablesException(message)
                    pass
            if not module:
                command = f'pip install goodtables-{name}'
                message = f'Plugin "{name}" is not installed. Run: "{command}"'
                raise exceptions.GoodtablesException()
            self.__plugins[name] = getattr(module, f'{name.capitalize()}Plugin')()
        return self.__plugins[name]


system = System()
