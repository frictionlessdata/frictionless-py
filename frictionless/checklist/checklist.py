from __future__ import annotations
import attrs
from typing import TYPE_CHECKING, List, Optional
from ..exception import FrictionlessException
from ..metadata import Metadata
from ..checks import baseline
from .check import Check
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from ..resource import Resource


# TODO: raise an exception if we try export a checklist with function based checks?
@attrs.define(kw_only=True)
class Checklist(Metadata):
    """Checklist representation.

    A class that combines multiple checks to be applied while validating
    a resource or package.

    """

    # State

    name: Optional[str] = None
    """
    A short name(preferably human-readable) for the Checklist.
    This MUST be lower-case and contain only alphanumeric characters
    along with "-" or "_".
    """

    title: Optional[str] = None
    """
    A human-readable title for the Checklist.
    """

    description: Optional[str] = None
    """
    A detailed description for the Checklist.
    """

    checks: List[Check] = attrs.field(factory=list)
    """
    List of checks to be applied during validation such as "deviated-cell", 
    "required-value" etc. 
    """

    pick_errors: List[str] = attrs.field(factory=list)
    """
    Specify the errors names to be picked while validation such as "sha256-count",
    "byte-count". Errors other than specified will be ignored.
    """

    skip_errors: List[str] = attrs.field(factory=list)
    """
    Specify the errors names to be skipped while validation such as "sha256-count", 
    "byte-count". Other errors will be included.
    """

    # Props

    @property
    def check_types(self) -> List[str]:
        return [check.type for check in self.checks]

    @property
    def scope(self) -> List[str]:
        scope = []
        basics: List[Check] = [baseline()]
        for check in basics + self.checks:
            for Error in check.Errors:
                if self.pick_errors:
                    if Error.type not in self.pick_errors and not set(
                        self.pick_errors
                    ).intersection(Error.tags):
                        continue
                if self.skip_errors:
                    if Error.type in self.skip_errors or set(
                        self.skip_errors
                    ).intersection(Error.tags):
                        continue
                scope.append(Error.type)
        return scope

    # Checks

    def add_check(self, check: Check) -> None:
        """Add new check to the schema"""
        self.checks.append(check)

    def has_check(self, type: str) -> bool:
        """Check if a check is present"""
        for check in self.checks:
            if check.type == type:
                return True
        return False

    def get_check(self, type: str) -> Check:
        """Get check by type"""
        for check in self.checks:
            if check.type == type:
                return check
        error = errors.ChecklistError(note=f'check "{type}" does not exist')
        raise FrictionlessException(error)

    def set_check(self, check: Check) -> Optional[Check]:
        """Set check by type"""
        if self.has_check(check.type):
            prev_check = self.get_check(check.type)
            index = self.checks.index(prev_check)
            self.checks[index] = check
            return prev_check
        self.add_check(check)

    def remove_check(self, type: str) -> Check:
        """Remove check by type"""
        check = self.get_check(type)
        self.checks.remove(check)
        return check

    def clear_checks(self) -> None:
        """Remove all the checks"""
        self.checks = []

    # Connect

    def connect(self, resource: Resource) -> List[Check]:
        checks = []
        basics: List[Check] = [baseline()]
        for check in basics + self.checks:
            check.connect(resource)
            checks.append(check)
        return checks

    # Match

    def match(self, error: errors.Error) -> bool:
        if isinstance(error, errors.DataError):
            if error.type not in self.scope:
                return False
        return True

    # Metadata

    metadata_type = "checklist"
    metadata_Error = errors.ChecklistError
    metadata_profile = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "pattern": settings.NAME_PATTERN},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "checks": {"type": "array"},
            "skipErrors": {"type": "array"},
            "pickErrors": {"type": "array"},
        },
    }

    @classmethod
    def metadata_specify(cls, *, type=None, property=None):
        if property == "checks":
            return Check
