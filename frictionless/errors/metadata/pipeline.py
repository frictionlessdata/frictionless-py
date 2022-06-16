from .metadata import MetadataError


class PipelineError(MetadataError):
    code = "pipeline-error"
    name = "Pipeline Error"
    template = "Pipeline is not valid: {note}"
    description = "Provided pipeline is not valid."


class StepError(PipelineError):
    code = "step-error"
    name = "Step Error"
    template = "Step is not valid: {note}"
    description = "Provided step is not valid"
