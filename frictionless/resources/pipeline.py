from ..report import Report
from ..pipeline import Pipeline
from .metadata import MetadataResource


class PipelineResource(MetadataResource):
    datatype = "pipeline"

    # Read

    def read_pipeline(self) -> Pipeline:
        return Pipeline.from_descriptor(self.descriptor, basepath=self.basepath)

    # Validate

    def validate(self, **options) -> Report:
        return Pipeline.validate_descriptor(self.descriptor, basepath=self.basepath)
