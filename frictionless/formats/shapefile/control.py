from __future__ import annotations

from typing import Optional

import attrs

from ...dialect import Control


@attrs.define(kw_only=True, repr=False)
class ShapefileControl(Control):
    """Shapefile control representation"""

    type = "shapefile"

    layer: Optional[str] = None
    """
    Name of the layer to read. A zip archive can contain several
    shapefiles, each of them is a layer. Defaults to the first layer.
    """

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "layer": {"type": "string"},
        },
    }
