from __future__ import annotations
from typing import Optional
from dataclasses import dataclass
from ..metadata2 import Metadata2
from ..checklist import Checklist
from ..dialect import Dialect
from ..schema import Schema
from ..resource import Resource
from ..package import Package
from ..report import Report
from .. import helpers
from ..file import File
from .. import errors


@dataclass
class InquiryTask(Metadata2):
    """Inquiry task representation."""

    # State

    descriptor: Optional[str] = None
    """# TODO: add docs"""

    type: Optional[str] = None
    """# TODO: add docs"""

    path: Optional[str] = None
    """# TODO: add docs"""

    name: Optional[str] = None
    """# TODO: add docs"""

    scheme: Optional[str] = None
    """# TODO: add docs"""

    format: Optional[str] = None
    """# TODO: add docs"""

    hashing: Optional[str] = None
    """# TODO: add docs"""

    encoding: Optional[str] = None
    """# TODO: add docs"""

    innerpath: Optional[str] = None
    """# TODO: add docs"""

    compression: Optional[str] = None
    """# TODO: add docs"""

    dialect: Optional[Dialect] = None
    """# TODO: add docs"""

    schema: Optional[Schema] = None
    """# TODO: add docs"""

    checklist: Optional[Checklist] = None
    """# TODO: add docs"""

    # Validate

    def validate(self, *, metadata=True):
        timer = helpers.Timer()

        # Detect type
        type = self.type
        if not type:
            type = "resource"
            if self.descriptor:
                file = File(self.descriptor)
                type = "package" if file.type == "package" else "resource"

        # Validate metadata
        if metadata and self.metadata_errors:
            errors = self.metadata_errors
            return Report.from_validation(time=timer.time, errors=errors)

        # Validate package
        if self.type == "package":
            package = Package(descriptor=self.descriptor)
            report = package.validate(self.checklist)
            return report

        # Validate resource
        resource = (
            Resource(
                path=self.path,
                scheme=self.scheme,
                format=self.format,
                hashing=self.hashing,
                encoding=self.encoding,
                innerpath=self.innerpath,
                compression=self.compression,
                dialect=self.dialect,
                schema=self.schema,
                # TODO: pass checklist here
            )
            if not self.descriptor
            # TODO: rebase on Resource.from_descriptor
            else Resource(descriptor=self.descriptor)
        )
        report = resource.validate(self.checklist)
        return report

    # Metadata

    metadata_Error = errors.InquiryError
    metadata_profile = {
        "properties": {
            "descriptor": {},
            "type": {},
            "path": {},
            "name": {},
            "scheme": {},
            "format": {},
            "hashing": {},
            "encoding": {},
            "innerpath": {},
            "compression": {},
            "dialect": {},
            "schema": {},
            "checklist": {},
        }
    }

    # TODO: validate type/descriptor matching
    def metadata_validate(self):
        yield from super().metadata_validate()
