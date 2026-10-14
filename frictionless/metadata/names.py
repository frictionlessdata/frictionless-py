from __future__ import annotations

import re
from typing import List, Optional

from .. import settings


def version_gate_notes(name: str, version: Optional[str]) -> List[str]:
    """Notes when a package or resource name breaks the v1 pattern under an explicit v1

    Datapackage v2 allows any string as the `name` of a package or a resource,
    while v1 restricts it to `settings.NAME_PATTERN`. As for missing values, the
    pattern is only checked when the version is explicitly resolved to v1; an
    undeclared version (`None`) stays lenient.
    """
    if version != "v1" or re.search(settings.NAME_PATTERN, name):
        return []
    return [f"{name!r} does not match {settings.NAME_PATTERN!r} at property 'name'"]
