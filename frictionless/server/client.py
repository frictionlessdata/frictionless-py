from typing import Any, Optional

from . import endpoints
from .project import Project


class Client:
    project: Project

    def __init__(self, folder: Optional[str] = None):
        self.project = Project(folder)

    def __call__(self, endpoint: str, **props: Any):
        package_name, module_name = endpoint.split("/")[1:]
        package = getattr(endpoints, package_name)
        module = getattr(package, module_name)
        return module.action(self.project, module.Props(**props))
