from __future__ import annotations
import attrs
from typing import Optional
from ...dialect import Control
from . import settings


@attrs.define(kw_only=True)
class SqlControl(Control):
    """SQL control representation"""

    type = "sql"

    # State

    table: Optional[str] = None
    """TODO: add docs"""

    prefix: str = settings.DEFAULT_PREFIX
    """TODO: add docs"""

    order_by: Optional[str] = None
    """TODO: add docs"""

    where: Optional[str] = None
    """TODO: add docs"""

    namespace: Optional[str] = None
    """TODO: add docs"""

    basepath: Optional[str] = None
    """TODO: add docs"""

    # Metadata

    metadata_profile = Control.metadata_merge(
        {
            "properties": {
                "table": {"type": "string"},
                "prefix": {"type": "string"},
                "order_by": {"type": "string"},
                "where": {"type": "string"},
                "namespace": {"type": "string"},
                "basepath": {"type": "string"},
            },
        }
    )
