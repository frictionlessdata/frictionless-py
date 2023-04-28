from typing import Optional
from .project import Project
from . import endpoints


class Client:
    project: Project

    def __init__(self, folder: Optional[str] = None):
        self.project = Project(folder)

    def invoke(self, endpoint, **props):
        package_name, module_name = endpoint.split("/")
        package = getattr(endpoints, package_name)
        module = getattr(package, module_name)
        return module.action(self.project, module.Props(**props))
