from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from .. import settings
from ..exception import FrictionlessException
from ..package import Package
from ..report import Report
from ..resource import Resource
from .metadata import MetadataResource

if TYPE_CHECKING:
    from .. import types
    from ..checklist import Checklist
    from ..pipeline import Pipeline


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
