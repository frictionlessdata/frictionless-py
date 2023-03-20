from __future__ import annotations
from typing import TYPE_CHECKING, Union, Optional, Type, TypeVar, Generic
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

if TYPE_CHECKING:
    from ..interfaces import IDescriptor
    from ..interfaces import ICallbackFunction

T = TypeVar("T", bound=Metadata)


class MetadataResource(JsonResource, Generic[T]):
    dataclass: Type[T]

    @property
    def descriptor(self) -> Union[IDescriptor, str]:
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
        on_row: Optional[ICallbackFunction] = None,
        parallel: bool = False,
        limit_rows: Optional[int] = None,
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    ) -> Report:
        return self.dataclass.validate_descriptor(self.descriptor, basepath=self.basepath)


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
