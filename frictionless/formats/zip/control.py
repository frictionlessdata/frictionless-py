from __future__ import annotations
import attrs
from typing import Optional, Any
from ...dialect import Control


@attrs.define(kw_only=True)
class ZipControl(Control):
    """Zip control representation"""

    type = "ckan"

    # State

    innerpath: Optional[str] = None
    """Where to find a data package. Defaults to 'datapackage.json/yaml'
    """

    compression: Optional[int] = None
    """the ZIP compression method to use when
        writing the archive. Possible values are the ones supported
        by Python's `zipfile` module. Defaults: zipfile.ZIP_DEFLATED
    """

    encoder_class: Optional[Any] = None
    """JSon endoder class
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {},
    }
