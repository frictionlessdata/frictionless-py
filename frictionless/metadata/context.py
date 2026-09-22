from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import attrs

if TYPE_CHECKING:
    from ..types import IStandards


@attrs.frozen
class ValidationContext:
    """Information shared down the recursion of `metadata_validate`

    A child descriptor is validated with a context derived from its parent's
    one (see `attrs.evolve`).
    """

    datapackage_version: Optional[IStandards] = None
    """
    Data Package standard version imposed by an ancestor's `$schema`
    (top-down inheritance). `None` when no ancestor declares one.
    """
