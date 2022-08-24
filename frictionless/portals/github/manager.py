from typing import Optional
from .control import GithubControl
from ...platform import platform
from ...resource import Resource
from ...package import Package
from ...package import Manager


class GithubManager(Manager[GithubControl]):

    # Read

    # TODO: implement
    def read_catalog(self):
        pass

    # TODO: improve
    def read_package(self, *, user: Optional[str] = None, repo: Optional[str] = None):
        client = platform.github.Github()
        user = user or self.control.user
        repo = repo or self.control.repo
        assert user
        assert repo
        location = "/".join([user, repo])
        repository = client.get_repo(location)
        branch = repository.default_branch
        contents = repository.get_contents("")
        paths = []
        while contents:
            file_content = contents.pop(0)  # type: ignore
            if file_content.type == "dir":
                contents.extend(repository.get_contents(file_content.path))  # type: ignore
            else:
                paths.append(file_content.path)
        package = Package()
        for path in paths:
            fullpath = f"https://raw.githubusercontent.com/{location}/{branch}/{path}"
            if path in ["datapackage.json", "datapackage.yaml"]:
                return Package.from_descriptor(fullpath)
            if path.endswith(".csv"):
                package.add_resource(Resource(path=fullpath))
        return package

    # Write
    # TODO: implement
