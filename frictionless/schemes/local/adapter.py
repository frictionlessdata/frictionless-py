from __future__ import annotations

import os
from typing import Any, Optional

from ... import helpers
from ...exception import FrictionlessException
from ...package import Package
from ...resource import Resource
from ...system import Adapter


class LocalAdapter(Adapter):
    def __init__(self, source: Any, *, basepath: Optional[str] = None):
        self.source = source
        self.basepath = basepath

    def read_package(self):
        # Directory
        if isinstance(self.source, str):
            normsource = helpers.join_basepath(self.source, basepath=self.basepath)
            if helpers.is_directory_source(normsource):
                name = "datapackage.json"
                path = os.path.join(normsource, name)  # type: ignore
                if os.path.isfile(path):
                    return Package.from_descriptor(path)

        # Expandable
        if helpers.is_expandable_source(self.source):
            package = Package(basepath=self.basepath)
            for path in helpers.expand_source(self.source, basepath=self.basepath):  # type: ignore
                package.add_resource(Resource(path=path))
            return package

        note = "Cannot read package"
        raise FrictionlessException(note)
