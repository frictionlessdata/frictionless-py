from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Generic, List, Optional, Type, TypeVar, Union

from .. import helpers, settings
from ..catalog import Catalog
from ..checklist import Checklist
from ..dialect import Dialect
from ..exception import FrictionlessException
from ..inquiry import Inquiry
from ..metadata import Metadata
from ..package import Package
from ..pipeline import Pipeline
from ..platform import platform
from ..report import Report
from ..resource import Resource
from ..schema import Schema
from .table import TableResource

if TYPE_CHECKING:
    from .. import types


T = TypeVar("T", bound=Metadata)


# TODO: support "resource.jsonSchema" (jsonschema validation)
class JsonResource(Resource):
    type = "json"
    datatype = "json"

    # Read

    # TODO: rebase on using loader
    def read_json(self) -> Any:
        """Read json data into memory

        Returns:
            any: json data
        """
        if self.data is not None:
            return self.data
        with helpers.ensure_open(self):
            text = self.read_text()
            return (
                platform.yaml.safe_load(text)
                if self.format == "yaml"
                else json.loads(text)
            )

    # Write

    # TODO: rebase on using loader
    def write_json(
        self, target: Optional[Union[JsonResource, Any]] = None, **options: Any
    ):
        """Write json data to the target"""
        resource = target
        if not isinstance(resource, Resource):
            resource = Resource(target, **options)
        if not isinstance(resource, JsonResource):
            raise FrictionlessException("target must be a json resource")
        data = self.read_json()
        dump = helpers.to_yaml if resource.format == "yaml" else helpers.to_json
        bytes = dump(data).encode("utf-8")
        assert resource.normpath
        helpers.write_file(resource.normpath, bytes, mode="wb")
        return resource


class ChartResource(JsonResource):
    datatype = "chart"


class JsonschemaResource(JsonResource):
    datatype = "jsonschema"


class MapResource(JsonResource):
    datatype = "map"


class ViewResource(JsonResource):
    datatype = "view"


class MetadataResource(JsonResource, Generic[T]):
    dataclass: Type[T]

    @property
    def descriptor(self) -> Union[types.IDescriptor, str]:
        descriptor = self.data if self.data is not None else self.path
        assert isinstance(descriptor, (str, dict))
        return descriptor

    # Read

    def read_metadata(self) -> T:
        return self.dataclass.from_descriptor(self.descriptor, basepath=self.basepath)

    # Validate

    def validate(
        self,
        checklist: Optional[Checklist] = None,
        *,
        name: Optional[str] = None,
        on_row: Optional[types.ICallbackFunction] = None,
        parallel: bool = False,
        limit_rows: Optional[int] = None,
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    ) -> Report:
        errors = []
        timer = helpers.Timer()
        try:
            self.read_metadata()
        except FrictionlessException as exception:
            errors = exception.reasons if exception.reasons else [exception.error]
        return platform.frictionless.Report.from_validation_task(
            self, time=timer.time, errors=errors
        )


class CatalogResource(MetadataResource[Catalog]):
    datatype = "catalog"
    dataclass = Catalog


class DialectResource(MetadataResource[Dialect]):
    datatype = "dialect"
    dataclass = Dialect


class SchemaResource(MetadataResource[Schema]):
    datatype = "schema"
    dataclass = Schema


class ChecklistResource(MetadataResource[Checklist]):
    datatype = "checklist"
    dataclass = Checklist


class PipelineResource(MetadataResource[Pipeline]):
    datatype = "pipeline"
    dataclass = Pipeline


class ReportResource(MetadataResource[Report]):
    datatype = "report"
    dataclass = Report


class ResourceResource(MetadataResource[Resource]):
    datatype = "resource"
    dataclass = Resource

    # Read

    def read_metadata(self) -> Resource:
        return self.dataclass.from_descriptor(
            self.descriptor,
            basepath=self.basepath,
            dialect=self.dialect or None,
            detector=self.detector or None,
        )

    # Extract

    def extract(
        self,
        *,
        name: Optional[str] = None,
        filter: Optional[types.IFilterFunction] = None,
        process: Optional[types.IProcessFunction] = None,
        limit_rows: Optional[int] = None,
    ) -> types.ITabularData:
        resource = self.read_metadata()
        if not isinstance(resource, TableResource):
            return {}
        return resource.extract(
            name=name, filter=filter, process=process, limit_rows=limit_rows
        )

    # List

    def list(self, *, name: Optional[str] = None) -> List[Resource]:
        """List dataset resources"""
        resource = self.read_metadata()
        return [resource]

    # Validate

    def validate(
        self,
        checklist: Optional[Checklist] = None,
        *,
        name: Optional[str] = None,
        on_row: Optional[types.ICallbackFunction] = None,
        parallel: bool = False,
        limit_rows: Optional[int] = None,
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    ) -> Report:
        try:
            resource = self.read_metadata()
        except FrictionlessException as exception:
            return Report.from_validation(errors=exception.to_errors())
        return resource.validate(
            checklist, limit_errors=limit_errors, limit_rows=limit_rows, on_row=on_row
        )


class PackageResource(MetadataResource[Package]):
    datatype = "package"
    dataclass = Package

    # Read

    def read_metadata(self) -> Package:
        return self.dataclass.from_descriptor(
            self.descriptor,
            basepath=self.basepath,
            dialect=self.dialect or None,
            detector=self.detector or None,
        )

    # Extract

    def extract(
        self,
        *,
        name: Optional[str] = None,
        filter: Optional[types.IFilterFunction] = None,
        process: Optional[types.IProcessFunction] = None,
        limit_rows: Optional[int] = None,
    ) -> types.ITabularData:
        package = self.read_metadata()
        return package.extract(
            name=name, filter=filter, process=process, limit_rows=limit_rows
        )

    # Index

    def index(self, database_url: str, **options: Any) -> List[str]:
        package = self.read_metadata()
        return package.index(database_url, **options)

    # List

    def list(self, *, name: Optional[str] = None) -> List[Resource]:
        package = self.read_metadata()
        return package.resources if name is None else [package.get_resource(name)]

    # Validate

    def validate(
        self,
        checklist: Optional[Checklist] = None,
        *,
        name: Optional[str] = None,
        on_row: Optional[types.ICallbackFunction] = None,
        parallel: bool = False,
        limit_rows: Optional[int] = None,
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    ) -> Report:
        try:
            package = self.read_metadata()
        except FrictionlessException as exception:
            return Report.from_validation(errors=exception.to_errors())
        return package.validate(
            checklist,
            name=name,
            parallel=parallel,
            limit_rows=limit_rows,
            limit_errors=limit_errors,
        )

    # Transform

    def transform(self, pipeline: Pipeline):
        package = self.read_metadata()
        return package.transform(pipeline)


class InquiryResource(MetadataResource[Inquiry]):
    datatype = "inquiry"
    dataclass = Inquiry

    # Validate

    def validate(
        self,
        checklist: Optional[Checklist] = None,
        *,
        name: Optional[str] = None,
        on_row: Optional[types.ICallbackFunction] = None,
        parallel: bool = False,
        limit_rows: Optional[int] = None,
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    ) -> Report:
        try:
            inquiry = self.read_metadata()
        except FrictionlessException as exception:
            return Report.from_validation(errors=exception.to_errors())
        return inquiry.validate(
            parallel=parallel,
        )
