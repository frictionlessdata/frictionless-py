from collections import namedtuple
from typing import Any, Dict, List, NamedTuple, Union
from github.ContentFile import ContentFile
from github.Repository import Repository
from .control import GithubControl
from ...exception import FrictionlessException
from ...catalog import Catalog
from ...package import Package
from ...package import Manager
from ...platform import platform
from ...resource import Resource


class GithubManager(Manager[GithubControl]):
    """Read and write data from/to Github"""

    # Read

    def read_catalog(self) -> Catalog:
        packages = []
        query: Dict[str, Any] = {}

        if self.control.repo or self.control.user or self.control.search:

            # Search single repo
            if self.control.user and self.control.repo:
                client = platform.github.Github(self.control.apikey)
                location = "/".join([self.control.user, self.control.repo])
                try:
                    repository = client.get_repo(location)
                except Exception as exception:
                    note = "Github API error" + repr(exception)
                    raise FrictionlessException(note)
                base_path = f"https://raw.githubusercontent.com/{location}/{repository.default_branch}"
                contents = repository.get_contents("")
                resource_path = get_resources(contents, repository)
                packages = get_packages(resource_path, base_path)
                if packages:
                    return Catalog(name="catalog", packages=packages)
                note = "Package/s not found"
                raise FrictionlessException(note)

            # Search multiple repos
            options = {}
            if self.control.search:
                query = {"q": self.control.search}
                if self.control.user and "user:" not in self.control.search:
                    options["user"] = self.control.user

            if not self.control.search and self.control.user:
                query = {"q": f"user:{self.control.user}"}

            if self.control.repo and "q" not in query:
                query["q"] = f"repo:{self.control.repo}"

            if self.control.order:
                options["order"] = self.control.order

            try:
                client = platform.github.Github(
                    self.control.apikey, per_page=self.control.per_page
                )
                repositories = client.search_repositories(query["q"], **options)
                if self.control.page:
                    repositories = repositories.get_page(self.control.page)
                for repository in repositories:
                    base_path = f"https://raw.githubusercontent.com/{repository.full_name}/{repository.default_branch}"
                    contents = repository.get_contents("")
                    resource_path = get_resources(contents, repository)
                    package = get_package(
                        resource_path, repository, base_path, self.control.formats
                    )
                    if package.resources:
                        packages.append(package)
            except Exception as exception:
                note = "Github API error" + repr(exception)
                raise FrictionlessException(note)

            if packages:
                return Catalog(name="catalog", packages=packages)

            note = "Package/s not found"
            raise FrictionlessException(note)

        note = "Repo or user or search text is required"
        raise FrictionlessException(note)

    def read_package(self) -> Package:
        assert self.control.user
        assert self.control.repo
        client = platform.github.Github(self.control.apikey)
        location = "/".join([self.control.user, self.control.repo])
        try:
            repository = client.get_repo(location)
        except Exception as exception:
            note = "Github API error" + repr(exception)
            raise FrictionlessException(note)
        base_path = (
            f"https://raw.githubusercontent.com/{location}/{repository.default_branch}"
        )
        contents = repository.get_contents("")
        resource_path = get_resources(contents, repository)
        package = get_package(resource_path, repository, base_path, self.control.formats)
        if package.resources:
            return package
        note = "Package/s not found"
        raise FrictionlessException(note)

    # Write

    def write_package(self, package: Package) -> NamedTuple:
        assert self.control.repo
        assert self.control.apikey

        # Create repo
        repository = None
        user = None
        try:
            client = platform.github.Github(self.control.apikey)
            user = client.get_user()
            repository = user.create_repo(
                name=self.control.repo, auto_init=True, gitignore_template="Python"
            )
        except Exception as exception:
            note = "Github API error:" + repr(exception)
            raise FrictionlessException(note)

        # Write package file to the repo
        file_created = None
        content = package.to_json()
        if content:
            newfile = self.control.filename or "datapackage.json"
            repository = user.get_repo(self.control.repo)
            email = user.email or self.control.email
            username = self.control.name or user.name or self.control.user
            assert email
            assert username
            try:
                author = platform.github.InputGitAuthor(username, email)
                file_created = repository.create_file(
                    path=newfile,
                    message="Create package.json",
                    content=content,
                    branch=repository.default_branch,
                    committer=author,
                    author=author,
                )
            except Exception as exception:
                note = "Github API error:" + repr(exception)
                raise FrictionlessException(note)

        response = namedtuple("response", ["repository", "file_created"])
        return response(repository, file_created)


def get_resources(
    contents: Union[List[ContentFile], ContentFile], repository: Repository
) -> List[str]:
    paths = []
    while contents:
        file_content = contents.pop(0)  # type: ignore
        if file_content.type == "dir":
            contents.extend(repository.get_contents(file_content.path))  # type: ignore
        else:
            paths.append(file_content.path)
    return paths


def get_packages(paths: List[str], base_path: str) -> List[Package]:
    packages = []
    for path in paths:
        fullpath = f"{base_path}/{path}"
        if path in ["datapackage.json", "datapackage.yaml"]:
            packages.append(Package.from_descriptor(fullpath))
    return packages


def get_package(
    paths: List[str], repository: Repository, base_path: str, formats: List[str]
) -> Package:
    package = Package(name=repository.name)
    for path in paths:
        fullpath = f"{base_path}/{path}"
        if path in ["datapackage.json", "datapackage.yaml"]:
            return Package.from_descriptor(fullpath)
        if any(path.endswith(ext) for ext in formats):
            resource = Resource(path=fullpath)
            resource.infer(sample=False)
            package.add_resource(resource)
    return package
