from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

from .. import settings

if TYPE_CHECKING:
    from ..types import IStandards


def validate_name(name: str, version: Optional[IStandards]) -> Optional[str]:
    """Note when a package or resource name breaks the v1 pattern

    Datapackage v2 allows any string as the `name` of a package or a resource,
    while v1 restricts it to `settings.NAME_PATTERN`. The pattern is only
    checked when the version is explicitly resolved to v1.
    """
    if version != "v1" or re.search(settings.NAME_PATTERN, name):
        return None
    return f"{name!r} does not match {settings.NAME_PATTERN!r} at property 'name'"
