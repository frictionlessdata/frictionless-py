from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .. import settings
from ..exception import FrictionlessException
from ..inquiry import Inquiry
from ..report import Report
from .metadata import MetadataResource

if TYPE_CHECKING:
    from .. import types
    from ..checklist import Checklist


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
