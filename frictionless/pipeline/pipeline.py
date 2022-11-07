from __future__ import annotations
import attrs
import warnings
from typing import Optional, List
from ..exception import FrictionlessException
from ..metadata import Metadata
from .step import Step
from .. import settings
from .. import errors


# TODO: raise an exception if we try export a pipeline with function based steps
@attrs.define(kw_only=True)
class Pipeline(Metadata):
    """Pipeline representation"""

    # State

    name: Optional[str] = None
    """
    A short url-usable (and preferably human-readable) name.
    This MUST be lower-case and contain only alphanumeric characters
    along with “_” or “-” characters.
    """

    title: Optional[str] = None
    """
    A human-oriented title for the Pipeline.
    """

    description: Optional[str] = None
    """
    A brief description of the Pipeline.
    """

    steps: List[Step] = attrs.field(factory=list)
    """
    List of transformation steps to apply. 
    """

    # Props

    @property
    def step_types(self) -> List[str]:
        """Return type list of the steps"""
        return [step.type for step in self.steps]

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

    metadata_type = "pipeline"
    metadata_Error = errors.PipelineError
    metadata_profile = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "steps": {"type": "array"},
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if property == "steps":
            return Step

    @classmethod
    def metadata_transform(cls, descriptor):
        super().metadata_transform(descriptor)

        # Tasks (framework/v4)
        tasks = descriptor.pop("tasks", [])
        if tasks and isinstance(tasks[0], dict):
            descriptor.setdefault("steps", tasks[0].get("steps"))
            note = 'Pipeline "tasks[].steps" is deprecated in favor of "steps"'
            note += "(it will be removed in the next major version)"
            warnings.warn(note, UserWarning)
