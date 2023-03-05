from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from ..exception import FrictionlessException
from ..report import Report
from ..resource import Resource
from .metadata import MetadataResource
from .. import settings

if TYPE_CHECKING:
    from ..checklist import Checklist
    from ..interfaces import ICallbackFunction
    from ..interfaces import IFilterFunction, IProcessFunction, ITabularData


class ResourceResource(MetadataResource):
    datatype = "resource"

    # Read

    def read_resource(self) -> Resource:
        return Resource.from_descriptor(self.descriptor, basepath=self.basepath)

    # Extract

    def extract(
        self,
        *,
        name: Optional[str] = None,
        filter: Optional[IFilterFunction] = None,
        process: Optional[IProcessFunction] = None,
        limit_rows: Optional[int] = None,
    ) -> ITabularData:
        resource = self.read_resource()
        return resource.extract(
            name=name, filter=filter, process=process, limit_rows=limit_rows
        )

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
        try:
            resource = self.read_resource()
        except FrictionlessException as exception:
            return Report.from_validation(errors=exception.to_errors())
        return resource.validate(
            checklist, limit_errors=limit_errors, limit_rows=limit_rows, on_row=on_row
        )
