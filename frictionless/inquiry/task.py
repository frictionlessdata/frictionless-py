from __future__ import annotations

import warnings
from typing import List, Optional

import attrs

from .. import errors, helpers, settings, types
from ..checklist import Checklist
from ..dialect import Dialect
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..package import Package
from ..report import Report
from ..resource import Resource
from ..schema import Schema
from ..system import system


# TODO: rebase back on using resource?
@attrs.define(kw_only=True, repr=False)
class InquiryTask(Metadata):
    """Inquiry task representation."""

    name: Optional[str] = None
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters.
    """

    type: Optional[str] = None
    """
    Type of the source to be validated such as "package", "resource" etc.
    """

    title: Optional[str] = None
    """
    A human-oriented title for the Inquiry.
    """

    description: Optional[str] = None
    """
    A brief description of the Inquiry.
    """

    path: Optional[str] = None
    """
    Path to the data source.
    """

    scheme: Optional[str] = None
    """
    Scheme for loading the file (file, http, ...). If not set, it'll be
    inferred from `source`.
    """

    format: Optional[str] = None
    """
    File source's format (csv, xls, ...). If not set, it'll be
    inferred from `source`.
    """

    encoding: Optional[str] = None
    """
    Source encoding. If not set, it'll be inferred from `source`.
    """

    mediatype: Optional[str] = None
    """
    Mediatype/mimetype of the resource e.g. “text/csv”, or “application/vnd.ms-excel”.
    Mediatypes are maintained by the Internet Assigned Numbers Authority (IANA) in a
    media type registry.
    """

    compression: Optional[str] = None
    """
    Source file compression (zip, ...). If not set, it'll be inferred from `source`.
    """

    extrapaths: Optional[List[str]] = None
    """
    List of paths to concatenate to the main path. It's used for multipart resources.
    """

    innerpath: Optional[str] = None
    """
    Path within the compressed file. It defaults to the first file in the archive
    (if the source is an archive).
    """

    dialect: Optional[Dialect] = None
    """
    Specific set of formatting parameters applied while reading data source.
    The parameters are set as a Dialect class. For more information, please
    check the Dialect Class documentation.
    """

    schema: Optional[Schema] = None
    """
    Schema descriptor. A string descriptor or path to schema file.
    """

    checklist: Optional[Checklist] = None
    """
    Checklist class with a set of validation checks to be applied to the
    data source being read. For more information, please check the
    Validation Checks documentation.
    """

    resource: Optional[str] = None
    """
    Resource descriptor. A string descriptor or path to resource file.
    """

    package: Optional[str] = None
    """
    Package descriptor. A string descriptor or path to package
    file.
    """

    # Validate

    def validate(self):
        timer = helpers.Timer()

        # Validate package
        if self.package:
            try:
                package = Package.from_descriptor(self.package)
            except FrictionlessException as exception:
                errors = exception.to_errors()
                return Report.from_validation(time=timer.time, errors=errors)
            report = package.validate()
            return report

        # Validate resource
        if self.resource:
            try:
                resource = Resource.from_descriptor(self.resource)
            except FrictionlessException as exception:
                errors = exception.to_errors()
                return Report.from_validation(time=timer.time, errors=errors)
            report = resource.validate()
            return report

        # Validate default
        try:
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
        except FrictionlessException as exception:
            errors = exception.to_errors()
            return Report.from_validation(time=timer.time, errors=errors)
        report = resource.validate()
        return report

    # Metadata

    metadata_type = "inquiry-task"
    metadata_Error = errors.InquiryTaskError
    metadata_profile = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "type": {"type": "string", "pattern": settings.TYPE_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
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
        },
    }

    @classmethod
    def metadata_select_property_class(cls, name: str):
        if name == "dialect":
            return Dialect
        elif name == "schema":
            return Schema
        elif name == "checklist":
            return Checklist

    @classmethod
    def metadata_transform(cls, descriptor: types.IDescriptor):
        # Source (framework/v4)
        source = descriptor.pop("source", None)
        if source:
            type = descriptor.pop("type", "resource")
            name = "resource" if type == "resource" else "package"
            descriptor.setdefault(name, source)
            note = 'InquiryTask "source" is deprecated in favor of "resource/package"'
            note += "(it will be removed in the next major version)"
            warnings.warn(note, UserWarning)

    @classmethod
    def metadata_validate(cls, descriptor: types.IDescriptor):  # type: ignore
        metadata_errors = list(super().metadata_validate(descriptor))
        if metadata_errors:
            yield from metadata_errors
            return

        # Security
        if not system.trusted:
            keys = ["path", "resource", "package"]
            for key in keys:
                value = descriptor.get(key)
                items = value if isinstance(value, list) else [value]  # type: ignore
                for item in items:  # type: ignore
                    if item and isinstance(item, str) and not helpers.is_safe_path(item):
                        yield errors.InquiryTaskError(note=f'path "{item}" is not safe')
                        return

        # Required
        path = descriptor.get("path")
        resource = descriptor.get("resource")
        package = descriptor.get("package")
        if path is None and resource is None and package is None:
            note = 'one of the properties "path", "resource", or "package" is required'
            yield errors.InquiryTaskError(note=note)
