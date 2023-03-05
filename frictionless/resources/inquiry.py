from ..report import Report
from ..inquiry import Inquiry
from .metadata import MetadataResource


class InquiryResource(MetadataResource):
    datatype = "inquiry"

    # Read

    def read_inquiry(self) -> Inquiry:
        return Inquiry.from_descriptor(self.descriptor, basepath=self.basepath)

    # Validate

    def validate(self, **options) -> Report:
        return Inquiry.validate_descriptor(self.descriptor, basepath=self.basepath)
