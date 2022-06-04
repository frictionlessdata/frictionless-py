from typing import TYPE_CHECKING, Optional, List, Any
from ..metadata import Metadata
from .validate import validate
from ..check import Check
from .. import settings
from .. import errors


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
    ):
        self.setinitial("checks", checks)
        self.setinitial("pickErrors", pick_errors)
        self.setinitial("skipErrors", skip_errors)
        self.setinitial("limitErrors", limit_errors)
        self.setinitial("limitMemory", limit_memory)
        self.setinitial("original", original)
        super().__init__(descriptor)

    @property
    def checks(self):
        return self.get("checks")

    @property
    def pick_errors(self):
        return self.get("pickErrors")

    @property
    def skip_errors(self):
        return self.get("skipErrors")

    @property
    def limit_errors(self):
        return self.get("limitErrors")

    @property
    def limit_memory(self):
        return self.get("limitMemory")

    @property
    def original(self):
        return self.get("original")

    # Metadata

    metadata_Error = errors.ChecklistError
    metadata_profile = settings.CHECKLIST_PROFILE
