from __future__ import annotations
from typing import TYPE_CHECKING, Union, Optional, Type, TypeVar, Generic
from ..exception import FrictionlessException
from ..platform import platform
from ..metadata import Metadata
from ..catalog import Catalog
from ..checklist import Checklist
from ..pipeline import Pipeline
from ..dialect import Dialect
from ..schema import Schema
from ..inquiry import Inquiry
from ..report import Report
from .json import JsonResource
from .. import settings
from .. import helpers

if TYPE_CHECKING:
    from .. import types

T = TypeVar("T", bound=Metadata)


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


class InquiryResource(MetadataResource[Inquiry]):
    datatype = "inquiry"
    dataclass = Inquiry


class ReportResource(MetadataResource[Report]):
    datatype = "report"
    dataclass = Report
