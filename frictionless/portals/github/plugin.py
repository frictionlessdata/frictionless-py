from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import urlparse

from ...system import Plugin
from .adapter import GithubAdapter
from .control import GithubControl

if TYPE_CHECKING:
    from ...dialect import Control


class GithubPlugin(Plugin):
    """Plugin for Github"""

    # Hooks

    def create_adapter(
        self,
        source: Any,
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
    ):
        if isinstance(source, str):
            parsed = urlparse(source)
            if not control or isinstance(control, GithubControl):
                if parsed.netloc == "github.com":
                    control = control or GithubControl()
                    splited_url = parsed.path.split("/")[1:]
                    if len(splited_url) == 1:
                        control.user = splited_url[0]
                        return GithubAdapter(control)
                    if len(splited_url) == 2:
                        control.user, control.repo = splited_url
                    return GithubAdapter(control)
        if source is None and isinstance(control, GithubControl):
            return GithubAdapter(control=control)

    def select_control_class(self, type: Optional[str] = None):
        if type == "github":
            return GithubControl
