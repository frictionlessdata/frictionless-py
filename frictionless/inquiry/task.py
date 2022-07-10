from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass
from ..metadata import Metadata
from ..checklist import Checklist
from ..dialect import Dialect
from ..schema import Schema
from ..resource import Resource
from ..package import Package
from ..report import Report
from .. import helpers
from .. import errors


@dataclass
class InquiryTask(Metadata):
    """Inquiry task representation."""

    # State

    path: Optional[str] = None
    """# TODO: add docs"""

    type: Optional[str] = None
    """# TODO: add docs"""

    scheme: Optional[str] = None
    """# TODO: add docs"""

    format: Optional[str] = None
    """# TODO: add docs"""

    hashing: Optional[str] = None
    """# TODO: add docs"""

    encoding: Optional[str] = None
    """# TODO: add docs"""

    compression: Optional[str] = None
    """# TODO: add docs"""

    extrapaths: Optional[List[str]] = None
    """# TODO: add docs"""

    innerpath: Optional[str] = None
    """# TODO: add docs"""

    dialect: Optional[Dialect] = None
    """# TODO: add docs"""

    schema: Optional[Schema] = None
    """# TODO: add docs"""

    checklist: Optional[Checklist] = None
    """# TODO: add docs"""

    resource: Optional[str] = None
    """# TODO: add docs"""

    package: Optional[str] = None
    """# TODO: add docs"""

    # Validate

    def validate(self, *, metadata=True):
        timer = helpers.Timer()

        # Validate metadata
        if metadata and self.metadata_errors:
            errors = self.metadata_errors
            return Report.from_validation(time=timer.time, errors=errors)

        # Validate package
        if self.package:
            package = Package.from_descriptor(self.package)
            report = package.validate()
            return report

        # Validate resource
        if self.resource:
            resource = Resource.from_descriptor(self.resource)
            report = resource.validate()
            return report

        # Validate default
        resource = Resource.from_options(
            path=self.path,
            type=self.type,
            scheme=self.scheme,
            format=self.format,
            hashing=self.hashing,
            encoding=self.encoding,
            compression=self.compression,
            extrapaths=self.extrapaths,
            innerpath=self.innerpath,
            dialect=self.dialect,
            schema=self.schema,
            checklist=self.checklist,
        )
        report = resource.validate()
        return report

    # Metadata

    metadata_Error = errors.InquiryTaskError
    metadata_Types = dict(dialect=Dialect, schema=Schema, checklist=Checklist)
    metadata_profile = {
        "properties": {
            "path": {},
            "type": {},
            "scheme": {},
            "format": {},
            "hashing": {},
            "encoding": {},
            "innerpath": {},
            "compression": {},
            "dialect": {},
            "schema": {},
            "checklist": {},
            "resource": {},
            "package": {},
        }
    }

    # TODO: validate type/descriptor matching
    def metadata_validate(self):
        yield from super().metadata_validate()
