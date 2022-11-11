from __future__ import annotations
from typing import TYPE_CHECKING
from ...platform import platform

if TYPE_CHECKING:
    from ..resource import Resource


def index(
    self: Resource,
):
    """Index resource into a database"""
    print(self)
    pass
