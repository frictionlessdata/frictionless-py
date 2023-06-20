from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .. import settings
from ..exception import FrictionlessException
from ..report import Report
from ..resource import Resource
from .metadata import MetadataResource
from .table import TableResource

if TYPE_CHECKING:
    from .. import types
    from ..checklist import Checklist


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
