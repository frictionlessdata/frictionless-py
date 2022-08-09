import os
from collections import namedtuple
from typing import Optional
from .control import GithubControl
from ...exception import FrictionlessException
from ...package import Package
from ...package import Manager
from ...platform import platform
from ...resource import Resource


class GithubManager(Manager[GithubControl]):

    # Read

    def read_catalog(self, user: Optional[str] = None, apikey: Optional[str] = None):
        client = platform.github.Github(apikey, per_page=self.control.per_page)
        user = user or self.control.user
        search = self.control.search or f"user:{user}"
        print(search)
        assert search
        if self.control.page:
            search = f"{search}&page={self.control.page}"

        # Search
        try:
            repositories = client.search_repositories(search)
        except Exception as exception:
            note = "Github API error" + repr(exception)
            raise FrictionlessException(note)
        packages = []
        for repository in repositories:
            branch = repository.default_branch
            base_path = (
                f"https://raw.githubusercontent.com/{repository.full_name}/{branch}"
            )
            contents = repository.get_contents("")
            paths = _get_contents(contents, repository)
            package = _get_package(paths, repository, base_path, self.control.formats)
            # add package which has resources
            if package.resources:
                packages.append(package)
        if packages:
            return packages
        note = "Package not found"
        raise FrictionlessException(note)

    def read_package(
        self,
        *,
        user: Optional[str] = None,
        repo: Optional[str] = None,
        apikey: Optional[str] = None,
    ):
        user = user or self.control.user
        repo = repo or self.control.repo
        assert user
        assert repo
        client = platform.github.Github(apikey)
        location = "/".join([user, repo])
        try:
            repository = client.get_repo(location)
        except Exception as exception:
            note = "Github API error" + repr(exception)
            raise FrictionlessException(note)
        branch = repository.default_branch
        base_path = f"https://raw.githubusercontent.com/{location}/{branch}"
        contents = repository.get_contents("")
        paths = _get_contents(contents, repository)
        package = _get_package(paths, repository, base_path, self.control.formats)
        if package.resources:
            return package
        note = "Package not found"
        raise FrictionlessException(note)

    # Write

    def write_package(
        self,
        *,
        email: Optional[str] = None,
        repo: Optional[str] = None,
        apikey: Optional[str] = None,
        filename: Optional[str] = None,
        content: Optional[str] = None,
        branch: Optional[str] = None,
    ):
        repo = repo or self.control.repo
        apikey = apikey or os.environ.get("GITHUB_ACCESS_TOKEN", None)
        assert repo
        assert apikey
        # Create repo
        repository = None
        user = None
        try:
            client = platform.github.Github(apikey)
            user = client.get_user()
            repository = user.create_repo(
                name=repo, auto_init=True, gitignore_template="Python"
            )
        except Exception as exception:
            note = "Github API error:" + repr(exception)
            raise FrictionlessException(note)

        # Write package file to the repo
        file_created = None
        if content:
            newfile = filename or "package.json"
            repository = user.get_repo(repo)
            email = (
                user.email or self.control.email or os.environ.get("GITHUB_EMAIL", None)
            )
            username = (
                user.name or self.control.user or os.environ.get("GITHUB_NAME", None)
            )
            assert email
            assert username
            try:
                author = platform.github.InputGitAuthor(username, email)
                branch = branch or repository.default_branch
                file_created = repository.create_file(
                    path=newfile,
                    message="Create package.json",
                    content=content,
                    branch=branch,
                    committer=author,
                    author=author,
                )
            except Exception as exception:
                note = "Github API error:" + repr(exception)
                raise FrictionlessException(note)

        response = namedtuple("response", ["repository", "file_created"])
        return response(repository, file_created)


def _get_contents(contents, repository):
    paths = []
    while contents:
        file_content = contents.pop(0)  # type: ignore
        if file_content.type == "dir":
            contents.extend(repository.get_contents(file_content.path))  # type: ignore
        else:
            paths.append(file_content.path)
    return paths


def _get_package(paths, repository, base_path, formats):
    package = Package(name=repository.name)
    for path in paths:
        fullpath = f"{base_path}/{path}"
        if path in ["datapackage.json", "datapackage.yaml"]:
            return Package.from_descriptor(fullpath)
        if any(path.endswith(ext) for ext in formats):
            package.add_resource(Resource(path=fullpath))
    return package
