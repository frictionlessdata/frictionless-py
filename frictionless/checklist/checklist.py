from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from ..metadata2 import Metadata2
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
class Checklist(Metadata2):
    validate = validate

    def __init__(
        self,
        *,
        checks: Optional[List[Check]] = None,
        pick_errors: Optional[List[str]] = None,
        skip_errors: Optional[List[str]] = None,
        limit_errors: Optional[int] = None,
        limit_memory: Optional[int] = None,
    ):
        self.checks = checks or []
        self.pick_errors = pick_errors or []
        self.skip_errors = skip_errors or []
        self.limit_errors = limit_errors or settings.DEFAULT_LIMIT_ERRORS
        self.limit_memory = limit_memory or settings.DEFAULT_LIMIT_ERRORS

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

    # Convert

    convert_properties = [
        "checks",
        "pick_errors",
        "skip_errors",
        "limit_errors",
        "limit_memory",
    ]

    @classmethod
    def from_descriptor(cls, descriptor):
        metadata = super().from_descriptor(descriptor)
        metadata.checks = [system.create_check(check) for check in metadata.checks]  # type: ignore
        return metadata

    # TODO: rebase on to_descriptor
    # TODO: make remove defaults nicer / support expand
    def to_descriptor(self):
        descriptor = super().to_descriptor()
        descriptor["checks"] = [check.to_dict() for check in self.checks]
        helpers.remove_default(descriptor, "pickErrors", [])
        helpers.remove_default(descriptor, "skipErrors", [])
        helpers.remove_default(descriptor, "limitErrors", settings.DEFAULT_LIMIT_ERRORS)
        helpers.remove_default(descriptor, "limitMemory", settings.DEFAULT_LIMIT_ERRORS)
        return descriptor

    # Metadata

    metadata_Error = errors.ChecklistError
    metadata_profile = settings.CHECKLIST_PROFILE

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Checks
        for check in self.checks:
            yield from check.metadata_errors
