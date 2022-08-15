from __future__ import annotations
import attrs
import os
from typing import Optional, List
from ...dialect import Control


@attrs.define(kw_only=True)
class GithubControl(Control):
    """Github control representation"""

    type = "github"

    # State

    apikey: Optional[str] = os.environ.get("GITHUB_ACCESS_TOKEN", None)
    """NOTE: add docs"""

    email: Optional[str] = os.environ.get("GITHUB_EMAIL", None)
    """NOTE: add docs"""

    formats: Optional[List[str]] = ["csv"]
    """NOTE: add docs"""

    name: Optional[str] = os.environ.get("GITHUB_NAME", None)
    """NOTE: add docs"""

    order: Optional[str] = None
    """NOTE: add docs"""

    page: Optional[int] = None
    """NOTE: add docs"""

    per_page: Optional[int] = 30
    """NOTE: add docs"""

    repo: Optional[str] = None
    """NOTE: add docs"""

    search: Optional[str] = None
    """NOTE: add docs"""

    sort: Optional[str] = None
    """NOTE: add docs"""

    user: Optional[str] = None
    """NOTE: add docs"""

    filename: Optional[str] = None
    """NOTE: add docs"""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "apikey": {"type": "string"},
            "email": {"type": "string"},
            "formats": {"type": "array"},
            "name": {"type": "string"},
            "order": {"type": "string"},
            "per_page": {"type": "int"},
            "page": {"type": "int"},
            "repo": {"type": "string"},
            "search": {"type": "str"},
            "sort": {"type": "string"},
            "user": {"type": "string"},
            "filename": {"type": "string"},
        },
    }
