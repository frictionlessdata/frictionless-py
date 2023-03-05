from ..report import Report
from .metadata import MetadataResource


class ReportResource(MetadataResource):
    datatype = "report"

    # Read

    def read_report(self) -> Report:
        return Report.from_descriptor(self.descriptor, basepath=self.basepath)

    # Validate

    def validate(self, **options) -> Report:
        return Report.validate_descriptor(self.descriptor, basepath=self.basepath)
