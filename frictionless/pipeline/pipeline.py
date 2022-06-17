from __future__ import annotations
from typing import List
from ..metadata2 import Metadata2
from .validate import validate
from ..step import Step
from .. import settings
from .. import errors


# TODO: raise an exception if we try export a pipeline with function based steps
class Pipeline(Metadata2):
    """Pipeline representation"""

    validate = validate

    def __init__(
        self,
        *,
        steps: List[Step] = [],
        limit_memory: int = settings.DEFAULT_LIMIT_MEMORY,
    ):
        self.steps = steps.copy()
        self.limit_memory = limit_memory

    steps: List[Step]
    """List of transform steps"""

    limit_memory: int
    """TODO: add docs"""

    @property
    def step_codes(self) -> List[str]:
        return [step.code for step in self.steps]

    # Metadata

    metadata_Error = errors.PipelineError
    metadata_profile = settings.PIPELINE_PROFILE
    metadata_properties = [
        {"name": "steps", "type": Step},
        {"name": "limitMemory", "default": settings.DEFAULT_LIMIT_MEMORY},
    ]

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Steps
        for step in self.steps:
            yield from step.metadata_errors
