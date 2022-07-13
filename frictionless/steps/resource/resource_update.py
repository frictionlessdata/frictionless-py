# type: ignore
from __future__ import annotations
from typing import Optional
from ...pipeline import Step
from ... import helpers


# NOTE:
# Some of the following step use **options - we need to review/fix it
# The step updating resource might benefit from having schema_patch argument


# TODO: rebase on dataclass
class resource_update(Step):
    """Update resource"""

    type = "resource-update"

    def __init__(
        self,
        *,
        name: str,
        new_name: Optional[str] = None,
        **options,
    ):
        self.name = name
        self.new_name = new_name
        self.descriptor = helpers.create_descriptor(**options)

    # State

    name: str
    """TODO: add docs"""

    new_name: Optional[str]
    """TODO: add docs"""

    descriptor: dict
    """TODO: add docs"""

    # Transform

    def transform_package(self, package):
        descriptor = self.descriptor.copy()
        if self.new_name:
            descriptor["name"] = self.new_name  # type: ignore
        resource = package.get_resource(self.name)
        resource.update(descriptor)

    # Metadata

    metadata_profile_patch = {
        "required": ["name"],
        "properties": {
            "name": {"type": "string"},
            "newName": {"type": "string"},
        },
    }
