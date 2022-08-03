from __future__ import annotations
import attrs
import warnings
from typing import Optional, List
from ..metadata import Metadata
from ..checklist import Checklist
from ..dialect import Dialect
from ..schema import Schema
from ..resource import Resource
from ..package import Package
from ..report import Report
from .. import settings
from .. import helpers
from .. import errors


@attrs.define
class InquiryTask(Metadata):
    """Inquiry task representation."""

    # State

    name: Optional[str] = None
    """NOTE: add docs"""

    type: Optional[str] = None
    """NOTE: add docs"""

    path: Optional[str] = None
    """NOTE: add docs"""

    scheme: Optional[str] = None
    """NOTE: add docs"""

    format: Optional[str] = None
    """NOTE: add docs"""

    encoding: Optional[str] = None
    """NOTE: add docs"""

    mediatype: Optional[str] = None
    """NOTE: add docs"""

    compression: Optional[str] = None
    """NOTE: add docs"""

    extrapaths: Optional[List[str]] = None
    """NOTE: add docs"""

    innerpath: Optional[str] = None
    """NOTE: add docs"""

    dialect: Optional[Dialect] = None
    """NOTE: add docs"""

    schema: Optional[Schema] = None
    """NOTE: add docs"""

    checklist: Optional[Checklist] = None
    """NOTE: add docs"""

    resource: Optional[str] = None
    """NOTE: add docs"""

    package: Optional[str] = None
    """NOTE: add docs"""

    strict: bool = False
    """NOTE: add docs"""

    # Validate

    def validate(self, *, metadata=True):
        timer = helpers.Timer()

        # Validate metadata
        if metadata:
            metadata_errors = self.list_metadata_errors()
            if metadata_errors:
                return Report.from_validation(time=timer.time, errors=metadata_errors)

        # Validate package
        if self.package:
            package = Package.from_descriptor(self.package)
            report = package.validate(strict=self.strict)
            return report

        # Validate resource
        if self.resource:
            resource = Resource.from_descriptor(self.resource)
            report = resource.validate(strict=self.strict)
            return report

        # Validate default
        resource = Resource.from_options(
            type=self.type,
            path=self.path,
            scheme=self.scheme,
            format=self.format,
            encoding=self.encoding,
            compression=self.compression,
            extrapaths=self.extrapaths,
            innerpath=self.innerpath,
            dialect=self.dialect,
            schema=self.schema,
            checklist=self.checklist,
        )
        report = resource.validate(strict=self.strict)
        return report

    # Metadata

    metadata_type = "inquiry-task"
    metadata_Error = errors.InquiryTaskError
    metadata_Types = dict(dialect=Dialect, schema=Schema, checklist=Checklist)
    metadata_profile = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "path": {"type": "string"},
            "scheme": {"type": "string"},
            "format": {"type": "string"},
            "encoding": {"type": "string"},
            "mediatype": {"type": "string"},
            "compression": {"type": "string"},
            "extrapaths": {"type": "array"},
            "innerpath": {"type": "string"},
            "dialect": {"type": ["object", "string"]},
            "schema": {"type": ["object", "string"]},
            "checklist": {"type": ["object", "string"]},
            "resource": {"type": ["object", "string"]},
            "package": {"type": ["object", "string"]},
            "strict": {"type": "boolean"},
        },
    }

    @classmethod
    def metadata_import(cls, descriptor):
        descriptor = cls.metadata_normalize(descriptor)

        # Source (framework_v4)
        source = descriptor.pop("source", None)
        if source:
            type = descriptor.pop("type", "resource")
            name = "resource" if type == "resource" else "package"
            descriptor.setdefault(name, source)
            note = 'InquiryTask "source" is deprecated in favor of "resource/package"'
            note += "(it will be removed in the next major version)"
            warnings.warn(note, UserWarning)

        return super().metadata_import(descriptor)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Required (normal)
        if self.path is None and self.resource is None and self.package is None:
            note = 'one of the properties "path", "resource", or "package" is required'
            yield errors.InquiryTaskError(note=note)
