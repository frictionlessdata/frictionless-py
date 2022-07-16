from typing import Optional
from .control import ZenodoControl
from ...resource import Resource
from ...package import Package
from ...package import Manager
from ... import helpers


class ZenodoManager(Manager[ZenodoControl]):

    # Read

    # TODO: implement
    def read_catalog(self):
        pass

    # TODO: implement
    def read_package(self, *, user: Optional[str] = None, repo: Optional[str] = None):
        pass

    # Write
    # TODO: implement
