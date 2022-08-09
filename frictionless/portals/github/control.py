from __future__ import annotations
import attrs
from typing import Optional
from ...dialect import Control


@attrs.define(kw_only=True)
class GithubControl(Control):
    """Github control representation"""

    type = "github"

    # State

    user: Optional[str] = None
    """NOTE: add docs"""

    email: Optional[str] = None
    """NOTE: add docs"""

    repo: Optional[str] = None
    """NOTE: add docs"""

    formats: Optional[list] = [".csv"]
    """NOTE: add docs"""

    search: Optional[str] = None
    """NOTE: add docs"""

    per_page: Optional[int] = 30
    """NOTE: add docs"""

    page: Optional[int] = None
    """NOTE: add docs"""

    apikey: Optional[str] = None
    """NOTE: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "user": {"type": "string"},
            "email": {"type": "string"},
            "repo": {"type": "string"},
            "formats": {"type": "array"},
            "search": {"type": "str"},
            "per_page": {"type": "int"},
            "page": {"type": "int"},
            "apikey": {"type": "string"},
        },
    }
