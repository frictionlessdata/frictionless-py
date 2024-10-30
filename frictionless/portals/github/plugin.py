from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple
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
        source: Optional[str],
        *,
        control: Optional[Control] = None,
        basepath: Optional[str] = None,
        packagify: bool = False,
    ) -> Optional[GithubAdapter]:
        if isinstance(source, str):
            parsed = urlparse(source)
            if not control or isinstance(control, GithubControl):
                if parsed.netloc == "github.com":
                    control = control or GithubControl()

                    control.user, control.repo = self._extract_user_and_repo(parsed.path)

                    return GithubAdapter(control)

        if source is None and isinstance(control, GithubControl):
            return GithubAdapter(control=control)

    def select_control_class(self, type: Optional[str] = None):
        if type == "github":
            return GithubControl

    @staticmethod
    def _extract_user_and_repo(url_path: str) -> Tuple[Optional[str], Optional[str]]:
        splitted_url = url_path.split("/")[1:]

        user = splitted_url[0] if len(splitted_url) >= 1 else None
        repo = splitted_url[1] if len(splitted_url) >= 2 else None

        return (user, repo)
