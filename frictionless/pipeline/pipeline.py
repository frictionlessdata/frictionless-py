from __future__ import annotations
from typing import List
from ..exception import FrictionlessException
from ..metadata2 import Metadata2
from .step import Step
from .. import settings
from .. import errors


# TODO: raise an exception if we try export a pipeline with function based steps
class Pipeline(Metadata2):
    """Pipeline representation"""

    def __init__(
        self,
        *,
        steps: List[Step] = [],
        limit_memory: int = settings.DEFAULT_LIMIT_MEMORY,
    ):
        self.steps = steps.copy()
        self.limit_memory = limit_memory

    # State

    steps: List[Step]
    """List of transform steps"""

    limit_memory: int
    """TODO: add docs"""

    # Props

    @property
    def step_codes(self) -> List[str]:
        return [step.code for step in self.steps]

    # Steps

    def add_step(self, step: Step) -> None:
        """Add new step to the schema"""
        self.steps.append(step)

    def has_step(self, code: str) -> bool:
        """Check if a step is present"""
        for step in self.steps:
            if step.code == code:
                return True
        return False

    def get_step(self, code: str) -> Step:
        """Get step by code"""
        for step in self.steps:
            if step.code == code:
                return step
        error = errors.SchemaError(note=f'step "{code}" does not exist')
        raise FrictionlessException(error)

    def set_step(self, code: str, step: Step) -> Step:
        """Set step by code"""
        prev_step = self.get_step(code)
        index = self.steps.index(prev_step)
        self.steps[index] = step
        return prev_step

    # Metadata

    metadata_Error = errors.PipelineError
    metadata_profile = {
        "properties": {
            "steps": {},
            "limitMemory": {},
        }
    }

    @classmethod
    def metadata_properties(cls):
        return super().metadata_properties(steps=Step)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Steps
        for step in self.steps:
            yield from step.metadata_errors
