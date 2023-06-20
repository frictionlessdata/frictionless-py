from __future__ import annotations

from typing import Any, Optional

import attrs

from ...dialect import Control


@attrs.define(kw_only=True, repr=False)
class ZipControl(Control):
    """Zip control representation"""

    type = "zip"

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
