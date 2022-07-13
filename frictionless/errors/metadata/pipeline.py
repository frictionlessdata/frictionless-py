from __future__ import annotations
from .metadata import MetadataError


class PipelineError(MetadataError):
    type = "pipeline-error"
    title = "Pipeline Error"
    description = "Provided pipeline is not valid."
    template = "Pipeline is not valid: {note}"


class StepError(PipelineError):
    type = "step-error"
    title = "Step Error"
    description = "Provided step is not valid"
    template = "Step is not valid: {note}"
