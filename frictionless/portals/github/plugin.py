from __future__ import annotations
from ...plugin import Plugin
from urllib.parse import urlparse
from .control import GithubControl
from .manager import GithubManager


# Plugin


class GithubPlugin(Plugin):
    """Plugin for Github"""

    # Hooks

    # TODO: improve
    def create_manager(self, source, *, control=None):
        if isinstance(source, str):
            parsed = urlparse(source)
            if not control or isinstance(control, GithubControl):
                if parsed.netloc == "github.com":
                    control = control or GithubControl()
                    user, repo = parsed.path.split("/")[1:]
                    control.user = user
                    if repo:
                        control.repo = repo
                    return GithubManager(control)

    def select_Control(self, type):
        if type == "github":
            return GithubControl
