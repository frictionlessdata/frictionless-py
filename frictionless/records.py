import attrs
from typing import Optional, List, Any


@attrs.define(kw_only=True)
class PathDetails:
    name: Optional[str] = None
    type: Optional[str] = None
    path: Optional[str] = None  # Remove optional in v6?
    data: Optional[Any] = None  # Remove in v6?
    scheme: Optional[str] = None
    format: Optional[str] = None
    mediatype: Optional[str] = None
    compression: Optional[str] = None
    extrapaths: Optional[List[str]] = None
    innerpath: Optional[str] = None
