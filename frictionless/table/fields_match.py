"""Arbitration between the `fieldsMatch` property and the deprecated `schema_sync`.

`schema_sync` predates the standard: it is the legacy spelling of what
datapackage v2 calls `partial`, so that is what it resolves to -- keeping the
behavior of the deprecated option unchanged. The deprecation note nonetheless
points users to `subset`, which is what they almost always mean by it (a schema
declaring only some of the data's columns); `partial` additionally tolerates
declared fields that the data does not carry.
"""

from __future__ import annotations

import warnings
from typing import Optional

from .. import types

DEFAULT: types.IFieldsMatch = "exact"

DEPRECATION_NOTE = (
    "The --schema-sync option is deprecated. Please use the fieldsMatch property "
    "introduced in datapackage v2 instead. "
    '(Set the value to "subset" to replicate the behavior of --schema-sync.)'
)

PRECEDENCE_NOTE = (
    'The "--schema-sync" option is ignored: the "fieldsMatch" property takes precedence.'
)


def resolve(
    declared: Optional[types.IFieldsMatch], *, schema_sync: bool
) -> types.IFieldsMatch:
    """Return the mode to apply, warning about the deprecated option.

    `declared` is the value the schema declares explicitly, `None` when it
    declares none. A declared value always wins over `schema_sync`, including
    when it is the default `exact` -- an explicit declaration is a decision.
    """
    if not schema_sync:
        return declared if declared is not None else DEFAULT

    if declared is not None:
        warnings.warn(PRECEDENCE_NOTE, UserWarning, stacklevel=2)
        return declared

    warnings.warn(DEPRECATION_NOTE, DeprecationWarning, stacklevel=2)
    return "partial"
