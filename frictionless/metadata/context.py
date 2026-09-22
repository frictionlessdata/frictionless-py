from __future__ import annotations

import secrets
from typing import TYPE_CHECKING, Dict, Optional

import attrs

if TYPE_CHECKING:
    from referencing import Resource

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

    json_schema_cache: Dict[str, Resource] = attrs.field(factory=dict)
    """
    JSON Schemas already retrieved during this validation, by URI (profiles
    and the "$ref"s they contain). Shared by all the derived contexts, so that
    a JSON Schema used by several descriptors is retrieved only once.
    """

    local_token: str = attrs.field(factory=lambda: secrets.token_hex(16))
    """
    Unguessable host of the "file:" URIs of local profiles. A "$ref" resolved
    against a local profile keeps it, which tells it apart from a "file:" URI
    written in a remote document (that cannot guess it).
    """
