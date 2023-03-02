from __future__ import annotations
import os
from typing import Any, Optional
from ...resource import Resource
from ...package import Package
from ... import helpers


class LocalAdapter:
    def __init__(self, source: Any, *, basepath: Optional[str] = None):
        self.source = source
        self.basepath = basepath

    def read_package(self):
        normsource = helpers.join_basepath(self.source, basepath=self.basepath)

        # Directory
        if helpers.is_directory_source(normsource):
            name = "datapackage.json"
            path = os.path.join(normsource, name)  # type: ignore
            if os.path.isfile(path):
                return Package.from_descriptor(path)

        # Expandable
        if helpers.is_expandable_source(normsource):
            package = Package()
            for path in helpers.expand_source(self.source, basepath=self.basepath):  # type: ignore
                package.add_resource(Resource(path=path))
            return package
