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
        """Checks if the source is meant to access a Github Data portal, and returns the adapter if applicable

        The source is expected to be in one of the formats :

        - https://github.com/user_or_org
        - https://github.com/user_or_org/repo

        Alternatively, user and/or repo information can be provided in the
        GithubControl, with an empty source.

        """
        if control and not isinstance(control, GithubControl):
            # Explicit control for other plugin
            return

        if source is None and isinstance(control, GithubControl):
            # Source informations are inside the control
            return GithubAdapter(control=control)

        if not isinstance(source, str):
            return

        parsed_url = urlparse(source)
        splited_url = parsed_url.path.split("/")[1:]

        has_expected_format = (
            parsed_url.netloc == "github.com"
            and len(splited_url) >= 1
            and len(splited_url) <= 2
        )

        if has_expected_format:
            control = control or GithubControl()
            control.user = splited_url[0]

            if len(splited_url) == 2:
                control.repo = splited_url[1]

            return GithubAdapter(control)

    def select_control_class(self, type: Optional[str] = None):
        if type == "github":
            return GithubControl
