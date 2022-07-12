from .metadata import MetadataError


class PipelineError(MetadataError):
    name = "Pipeline Error"
    type = "pipeline-error"
    template = "Pipeline is not valid: {note}"
    description = "Provided pipeline is not valid."


class StepError(PipelineError):
    name = "Step Error"
    type = "step-error"
    template = "Step is not valid: {note}"
    description = "Provided step is not valid"
