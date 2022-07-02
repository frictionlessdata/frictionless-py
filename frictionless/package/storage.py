from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .package import Package
    from ..resource import Resource


# NOTE:
# We might consider reducing this API to something like
# Storage.read/write_package although I have already made
# a few attempts using parser.write_row_stream to achieve this goal
# and this doesn't seem to work as storage.write_package needs to
# handle transactions and relation order in e.g. SQL plugin.
# So, as for now, we will continue to call Storage API
# from Parser API for plugin where there is a storage.


class Storage:
    def __init__(self, source, **options):
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()

    # Read

    def read_resource(self, name: str, **options) -> Resource:
        raise NotImplementedError()

    def read_package(self, **options) -> Package:
        raise NotImplementedError()

    # Write

    def write_resource(self, resource: Resource, *, force=False, **options):
        raise NotImplementedError()

    def write_package(self, package: Package, *, force=False, **options):
        raise NotImplementedError()

    # Delete

    def delete_resource(self, name: str, *, ignore=False, **options):
        raise NotImplementedError()

    def delete_package(self, names: List[str], *, ignore=False, **options):
        raise NotImplementedError()
