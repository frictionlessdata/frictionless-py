from __future__ import annotations
from typing import Optional, List
from importlib import import_module
from dataclasses import dataclass, field
from ..exception import FrictionlessException
from ..metadata import Metadata
from .step import Step
from .. import helpers
from .. import errors


# TODO: raise an exception if we try export a pipeline with function based steps
@dataclass
class Pipeline(Metadata):
    """Pipeline representation"""

    # State

    steps: List[Step] = field(default_factory=list)
    """List of transform steps"""

    # Props

    @property
    def step_codes(self) -> List[str]:
        return [step.code for step in self.steps]

    # Validate

    def validate(self):
        timer = helpers.Timer()
        errors = self.metadata_errors
        Report = import_module("frictionless").Report
        return Report.from_validation(time=timer.time, errors=errors)

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
        error = errors.PipelineError(note=f'step "{code}" does not exist')
        raise FrictionlessException(error)

    def set_step(self, step: Step) -> Optional[Step]:
        """Set step by code"""
        if self.has_step(step.code):
            prev_step = self.get_step(step.code)
            index = self.steps.index(prev_step)
            self.steps[index] = step
            return prev_step
        self.add_step(step)

    def remove_step(self, code: str) -> Step:
        """Remove step by code"""
        step = self.get_step(code)
        self.steps.remove(step)
        return step

    def clear_steps(self) -> None:
        """Remove all the steps"""
        self.steps = []

    # Metadata

    metadata_Error = errors.PipelineError
    metadata_profile = {
        "properties": {
            "steps": {},
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
