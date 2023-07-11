from __future__ import annotations

from ..exception import FrictionlessException
from ..inquiry import Inquiry
from ..report import Report
from .metadata import MetadataResource


class InquiryResource(MetadataResource[Inquiry]):
    datatype = "inquiry"
    dataclass = Inquiry

    # Read

    def read_metadata(self) -> Inquiry:
        return self.dataclass.from_descriptor(
            self.descriptor,
            basepath=self.basepath,
            dialect=self.dialect or None,
            detector=self.detector or None,
        )

    # Validate

    def validate(  # type: ignore
        self,
        *,
        parallel: bool = False,
    ) -> Report:
        try:
            inquiry = self.read_metadata()
        except FrictionlessException as exception:
            return Report.from_validation(errors=exception.to_errors())
        return inquiry.validate(
            parallel=parallel,
        )
