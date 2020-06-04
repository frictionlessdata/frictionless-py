#  import gunicorn
from ..plugin import Plugin
from ..server import Server


# Plugin


class ServerPlugin(Plugin):
    def create_server(self, name):
        if name == 'server/validation':
            return ValidationServer()


# Servers


class ValidationServer(Server):
    def listen(self, port):
        pass
