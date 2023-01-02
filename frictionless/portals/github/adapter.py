from __future__ import annotations
import os
from typing import TYPE_CHECKING, Any, Dict, List, Union
from .control import GithubControl
from ...system import Adapter
from ...exception import FrictionlessException
from ...catalog import Catalog
from ...package import Package
from ...platform import platform
from ...resource import Resource

if TYPE_CHECKING:
    from github.ContentFile import ContentFile
    from github.Repository import Repository


class GithubAdapter(Adapter):
    """Read and write data from/to Github"""

    def __init__(self, control: GithubControl):
        self.control = control

    # Read

    def read_catalog(self) -> Catalog:
        packages: List[Union[Package, str]] = []
        query: Dict[str, Any] = {}

        if not (self.control.repo or self.control.user or self.control.search):
            note = "Repo or user or search text is required"
            raise FrictionlessException(note)

        assert self.control.formats

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
            all_packages = get_package(
                resource_path, repository, base_path, self.control.formats, catalog=True
            )
            if all_packages and isinstance(all_packages, List):
                packages = packages + all_packages  # type: ignore
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

        if self.control.sort:
            options["sort"] = self.control.sort

        try:
            assert self.control.per_page
            assert self.control.formats
            client = platform.github.Github(
                self.control.apikey, per_page=self.control.per_page
            )
            user = client.get_user()
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
                if isinstance(package, Package) and package.resources:
                    packages.append(package)
        except Exception as exception:
            note = "Github API error" + repr(exception)
            raise FrictionlessException(note)

        if packages:
            return Catalog(name=user.name, packages=packages)

        note = "Package/s not found"
        raise FrictionlessException(note)

    def read_package(self) -> Package:
        if not (self.control.repo and self.control.user):
            note = "Repo and user is required"
            raise FrictionlessException(note)

        assert self.control.formats
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

        if isinstance(package, Package) and package.resources:
            return package

        note = "Package/s not found"
        raise FrictionlessException(note)

    # Write

    def write_package(self, package: Package) -> Repository:
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

        # Write package file
        content = package.to_json()
        package_path = self.control.filename or "datapackage.json"
        if self.control.basepath:
            package_path = os.path.join(self.control.basepath, package_path)
        repository = user.get_repo(self.control.repo)
        email = user.email or self.control.email
        username = self.control.name or user.name or self.control.user
        assert email
        assert username
        author = platform.github.InputGitAuthor(username, email)
        branch = repository.default_branch
        try:
            repository.create_file(
                path=package_path,
                message="Create package.json",
                content=content,
                branch=repository.default_branch,
                committer=author,
                author=author,
            )
        except Exception as exception:
            note = "Github API error:" + repr(exception)
            raise FrictionlessException(note)

        # Write resource files
        try:
            for resource in package.resources:
                resource_path = resource.path or ""
                if self.control.basepath:
                    resource_path = os.path.join(self.control.basepath, resource_path)
                repository.create_file(
                    path=resource_path,
                    message="Create package.json",
                    content=str(resource.read_bytes()),
                    branch=branch,
                    committer=author,
                    author=author,
                )
        except Exception as exception:
            note = "Github API error:" + repr(exception)
            raise FrictionlessException(note)

        return repository


def get_resources(
    contents: Union[List[ContentFile], ContentFile], repository: Repository
) -> List[ContentFile]:
    paths = []
    while contents:
        file_content = contents.pop(0)  # type: ignore
        if file_content.type == "dir":
            contents.extend(repository.get_contents(file_content.path))  # type: ignore
        else:
            paths.append(file_content)
    return paths


def get_package(
    paths: List[ContentFile],
    repository: Repository,
    base_path: str,
    formats: List[str],
    catalog: bool = False,
) -> Union[Package, List[Package]]:
    def multiple_packages(base_path):
        packages = []
        for file in paths:
            fullpath = f"{base_path}/{file.path}"
            if any(
                file.path.endswith(filename)
                for filename in ["datapackage.json", "datapackage.yaml"]
            ):
                package = Package.from_descriptor(fullpath)
                packages.append(package)
        return packages

    if catalog:
        return multiple_packages(base_path)

    package = Package(name=repository.name)
    for file in paths:
        fullpath = f"{base_path}/{file.path}"
        if file.path in ["datapackage.json", "datapackage.yaml"]:
            package = Package.from_descriptor(fullpath)
            return package
        if any(file.path.endswith(ext) for ext in formats):
            resource = Resource(path=file.path, basepath=base_path)
            resource.infer(sample=False)
            package.add_resource(resource)
    return package
