from __future__ import annotations
from typing import Optional, List, Any
from ..metadata import Metadata
from .validate import validate
from ..system import system
from ..step import Step
from .. import settings
from .. import helpers
from .. import errors


# TODO: raise an exception if we try export a pipeline with function based steps
class Pipeline(Metadata):
    validate = validate

    def __init__(
        self,
        descriptor: Optional[Any] = None,
        *,
        steps: Optional[List[Step]] = None,
        # TODO: implement
        limit_memory: Optional[int] = None,
        allow_parallel: Optional[bool] = None,
    ):
        self.setinitial("steps", steps)
        self.setinitial("limitMemory", limit_memory)
        self.setinitial("allowParallel", allow_parallel)
        super().__init__(descriptor)

    @property
    def steps(self) -> List[Step]:
        return self.get("steps", [])

    @property
    def step_codes(self) -> List[str]:
        return [step.code for step in self.steps]

    @property
    def limit_memory(self) -> bool:
        return self.get("limitMemory", settings.DEFAULT_LIMIT_MEMORY)

    @property
    def allow_parallel(self) -> bool:
        return self.get("allowParallel", False)

    # Metadata

    metadata_Error = errors.PipelineError
    metadata_profile = settings.PIPELINE_PROFILE

    def metadata_process(self):

        # Steps
        steps = self.get("steps")
        if isinstance(steps, list):
            for index, step in enumerate(steps):
                if not isinstance(step, Step):
                    step = system.create_step(step)
                    list.__setitem__(steps, index, step)
            if not isinstance(steps, helpers.ControlledList):
                steps = helpers.ControlledList(steps)
                steps.__onchange__(self.metadata_process)
                dict.__setitem__(self, "steps", steps)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Steps
        for step in self.steps:
            yield from step.metadata_errors
