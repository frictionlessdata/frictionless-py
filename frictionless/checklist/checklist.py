from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Any
from ..helpers import cached_property
from ..metadata import Metadata
from .validate import validate
from ..checks import baseline
from ..system import system
from ..check import Check
from .. import settings
from .. import helpers
from .. import errors

if TYPE_CHECKING:
    from ..resource import Resource


# TODO: raise an exception if we try export a checklist with function based checks
class Checklist(Metadata):
    validate = validate

    def __init__(
        self,
        descriptor: Optional[Any] = None,
        *,
        checks: Optional[List[Check]] = None,
        pick_errors: Optional[List[str]] = None,
        skip_errors: Optional[List[str]] = None,
        limit_errors: Optional[int] = None,
        limit_memory: Optional[int] = None,
        keep_original: Optional[bool] = None,
        allow_parallel: Optional[bool] = None,
    ):
        self.setinitial("checks", checks)
        self.setinitial("pickErrors", pick_errors)
        self.setinitial("skipErrors", skip_errors)
        self.setinitial("limitErrors", limit_errors)
        self.setinitial("limitMemory", limit_memory)
        self.setinitial("keepOriginal", keep_original)
        self.setinitial("allowParallel", allow_parallel)
        super().__init__(descriptor)

    @property
    def checks(self) -> List[Check]:
        return self.get("checks", [])

    @property
    def check_codes(self) -> List[str]:
        return [check.code for check in self.checks]

    @property
    def pick_errors(self) -> List[str]:
        return self.get("pickErrors", [])

    @property
    def skip_errors(self) -> List[str]:
        return self.get("skipErrors", [])

    @property
    def limit_errors(self) -> int:
        return self.get("limitErrors", settings.DEFAULT_LIMIT_ERRORS)

    @property
    def limit_memory(self) -> int:
        return self.get("limitMemory", settings.DEFAULT_LIMIT_MEMORY)

    @property
    def keep_original(self) -> bool:
        return self.get("keepOriginal", False)

    @property
    def allow_parallel(self) -> bool:
        return self.get("allowParallel", False)

    @cached_property
    def scope(self) -> List[str]:
        scope = []
        basics: List[Check] = [baseline()]
        for check in basics + self.checks:
            for Error in check.Errors:
                if self.pick_errors:
                    if Error.code not in self.pick_errors and not set(
                        self.pick_errors
                    ).intersection(Error.tags):
                        continue
                if self.skip_errors:
                    if Error.code in self.skip_errors or set(
                        self.skip_errors
                    ).intersection(Error.tags):
                        continue
                scope.append(Error.code)
        return scope

    # Connect

    def connect(self, resource: Resource) -> List[Check]:
        checks = []
        basics: List[Check] = [baseline()]
        for check in basics + self.checks:
            if check.metadata_valid:
                check = check.to_copy()
                check.connect(resource)
                checks.append(check)
        return checks

    # Match

    def match(self, error: errors.Error) -> bool:
        if error.tags.count("#data"):
            if error.code not in self.scope:
                return False
        return True

    # Metadata

    metadata_Error = errors.ChecklistError
    metadata_profile = settings.CHECKLIST_PROFILE

    def metadata_process(self):

        # Checks
        checks = self.get("checks")
        if isinstance(checks, list):
            for index, check in enumerate(checks):
                if not isinstance(check, Check):
                    check = system.create_check(check)
                    list.__setitem__(checks, index, check)
            if not isinstance(checks, helpers.ControlledList):
                checks = helpers.ControlledList(checks)
                checks.__onchange__(self.metadata_process)
                dict.__setitem__(self, "checks", checks)

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Checks
        for check in self.checks:
            yield from check.metadata_errors
