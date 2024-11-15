from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional, Tuple
from urllib.parse import urlparse

from ...exception import FrictionlessException
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

                    user, repo = self._extract_user_and_repo(parsed.path)

                    self._assert_no_mismatch(user, control.user, "user")
                    self._assert_no_mismatch(repo, control.repo, "repo")

                    control.user = user
                    control.repo = repo

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

    @staticmethod
    def _assert_no_mismatch(
        value: Optional[str],
        control_value: Optional[str],
        user_or_repo: Literal["user", "repo"],
    ):
        if value and control_value and control_value != value:
            raise FrictionlessException(
                f'Mismatch between url and provided "{user_or_repo}"'
                f"information (in url: {value}), in control: {control_value}"
            )
