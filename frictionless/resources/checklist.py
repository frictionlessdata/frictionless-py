from ..report import Report
from ..checklist import Checklist
from .metadata import MetadataResource


class ChecklistResource(MetadataResource):
    datatype = "checklist"

    # Read

    def read_checklist(self) -> Checklist:
        return Checklist.from_descriptor(self.descriptor, basepath=self.basepath)

    # Validate

    def validate(self, **options) -> Report:
        return Checklist.validate_descriptor(self.descriptor, basepath=self.basepath)
