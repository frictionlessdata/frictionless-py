from typing import TYPE_CHECKING, Optional, List, Any
from ..helpers import cached_property
from ..metadata import Metadata
from .validate import validate
from ..checks import baseline
from ..check import Check
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from ..resource import Resource


class Checklist(Metadata):
    validate = validate

    def __init__(
        self,
        descriptor: Optional[Any] = None,
        *,
        checks: Optional[List[Check]] = None,
        pick_errors: Optional[List[str]] = None,
        skip_errors: Optional[List[str]] = None,
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
        limit_memory: int = settings.DEFAULT_LIMIT_MEMORY,
        original: bool = False,
        parallel: bool = False,
    ):
        self.setinitial("checks", checks)
        self.setinitial("pickErrors", pick_errors)
        self.setinitial("skipErrors", skip_errors)
        self.setinitial("limitErrors", limit_errors)
        self.setinitial("limitMemory", limit_memory)
        self.setinitial("original", original)
        self.setinitial("parallel", parallel)
        self.__baseline = baseline()
        super().__init__(descriptor)

    @property
    def checks(self):
        return [self.__baseline] + self.get("checks", [])

    @property
    def pick_errors(self):
        return self.get("pickErrors", [])

    @property
    def skip_errors(self):
        return self.get("skipErrors", [])

    @property
    def limit_errors(self):
        return self.get("limitErrors")

    @property
    def limit_memory(self):
        return self.get("limitMemory")

    @property
    def original(self):
        return self.get("original")

    @property
    def parallel(self):
        return self.get("parallel")

    @cached_property
    def scope(self):
        scope = []
        for check in self.checks:
            for Error in check.Errors:
                if Error.code in self.skip_errors:
                    continue
                if Error.code not in self.pick_errors and self.pick_errors:
                    continue
                scope.append(Error.code)
        return scope

    # Connect

    def connect(self, resource: Resource) -> List[Check]:
        checks = []
        for check in self.checks:
            if check.metadata_valid:
                check = check.to_copy()
                check.connect(resource)
                checks.append(check)
        return checks

    # Metadata

    metadata_Error = errors.ChecklistError
    metadata_profile = settings.CHECKLIST_PROFILE

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Tasks
        for check in self.checks:
            yield from check.metadata_errors
