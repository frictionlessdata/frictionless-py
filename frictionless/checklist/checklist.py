from __future__ import annotations
from typing import TYPE_CHECKING, List
from ..metadata2 import Metadata2
from .validate import validate
from ..checks import baseline
from ..check import Check
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from ..resource import Resource


# TODO: raise an exception if we try export a checklist with function based checks
class Checklist(Metadata2):
    validate = validate

    def __init__(
        self,
        *,
        checks: List[Check] = [],
        pick_errors: List[str] = [],
        skip_errors: List[str] = [],
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
        limit_memory: int = settings.DEFAULT_LIMIT_ERRORS,
    ):
        self.checks = checks.copy()
        self.pick_errors = pick_errors.copy()
        self.skip_errors = skip_errors.copy()
        self.limit_errors = limit_errors
        self.limit_memory = limit_memory

    # Properties

    checks: List[Check]
    """# TODO: add docs"""

    pick_errors: List[str]
    """# TODO: add docs"""

    skip_errors: List[str]
    """# TODO: add docs"""

    limit_errors: int
    """# TODO: add docs"""

    limit_memory: int
    """# TODO: add docs"""

    @property
    def check_codes(self) -> List[str]:
        return [check.code for check in self.checks]

    @property
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
                # TODO: review
                #  check = check.to_copy()
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
    metadata_properties = [
        {"name": "checks", "type": Check},
        {"name": "pickErrors", "default": []},
        {"name": "skipErrors", "default": []},
        {"name": "limitErrors", "default": settings.DEFAULT_LIMIT_ERRORS},
        {"name": "limitMemory", "default": settings.DEFAULT_LIMIT_MEMORY},
    ]

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Checks
        for check in self.checks:
            yield from check.metadata_errors
