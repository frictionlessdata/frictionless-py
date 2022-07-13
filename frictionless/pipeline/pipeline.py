from __future__ import annotations
import attrs
from typing import Optional, List
from importlib import import_module
from ..exception import FrictionlessException
from ..metadata import Metadata
from .step import Step
from .. import helpers
from .. import errors


# TODO: raise an exception if we try export a pipeline with function based steps
@attrs.define(kw_only=True)
class Pipeline(Metadata):
    """Pipeline representation"""

    # State

    name: Optional[str] = None
    """# TODO: add docs"""

    title: Optional[str] = None
    """TODO: add docs"""

    description: Optional[str] = None
    """TODO: add docs"""

    steps: List[Step] = attrs.field(factory=list)
    """List of transform steps"""

    # Props

    @property
    def step_types(self) -> List[str]:
        return [step.type for step in self.steps]

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

    def has_step(self, type: str) -> bool:
        """Check if a step is present"""
        for step in self.steps:
            if step.type == type:
                return True
        return False

    def get_step(self, type: str) -> Step:
        """Get step by type"""
        for step in self.steps:
            if step.type == type:
                return step
        error = errors.PipelineError(note=f'step "{type}" does not exist')
        raise FrictionlessException(error)

    def set_step(self, step: Step) -> Optional[Step]:
        """Set step by type"""
        if self.has_step(step.type):
            prev_step = self.get_step(step.type)
            index = self.steps.index(prev_step)
            self.steps[index] = step
            return prev_step
        self.add_step(step)

    def remove_step(self, type: str) -> Step:
        """Remove step by type"""
        step = self.get_step(type)
        self.steps.remove(step)
        return step

    def clear_steps(self) -> None:
        """Remove all the steps"""
        self.steps = []

    # Metadata

    metadata_Error = errors.PipelineError
    metadata_Types = dict(steps=Step)
    metadata_profile = {
        "properties": {
            "name": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "steps": {},
        }
    }

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Steps
        for step in self.steps:
            yield from step.metadata_errors
