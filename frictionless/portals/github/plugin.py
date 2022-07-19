from __future__ import annotations
from ...plugin import Plugin
from urllib.parse import urlparse
from .control import GithubControl
from .manager import GithubManager


# Plugin


class GithubPlugin(Plugin):
    """Plugin for Github"""

    # Hooks

    def create_control(self, descriptor):
        if descriptor.get("type") == "github":
            return GithubControl.from_descriptor(descriptor)

    # TODO: improve
    def create_manager(self, source, *, control=None):
        parsed = urlparse(source)
        if isinstance(source, str):
            if not control or isinstance(control, GithubControl):
                if parsed.netloc == "github.com":
                    control = control or GithubControl()
                    user, repo = parsed.path.split("/")[1:]
                    control.user = user
                    if repo:
                        control.repo = repo
                    return GithubManager(control)
