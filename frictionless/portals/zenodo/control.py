from __future__ import annotations
import attrs
from typing import Optional
from ...dialect import Control


@attrs.define(kw_only=True)
class ZenodoControl(Control):
    """Zenodo control representation"""

    type = "github"

    user: Optional[str] = None
    """TODO: add docs"""

    repo: Optional[str] = None
    """TODO: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "user": {"type": "string"},
            "repo": {"type": "string"},
        },
    }
