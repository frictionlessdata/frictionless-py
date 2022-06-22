from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass, field
from ..metadata2 import Metadata2
from .describe import describe
from .validate import validate
from .. import settings
from .. import errors


@dataclass
class Dialect(Metadata2):
    """Dialect representation"""

    describe = describe
    validate = validate

    # Properties

    header_rows: List[int] = field(default_factory=lambda: settings.DEFAULT_HEADER_ROWS)
    """TODO: add docs"""

    header_join: str = settings.DEFAULT_HEADER_JOIN
    """TODO: add docs"""

    header_case: bool = settings.DEFAULT_HEADER_CASE
    """TODO: add docs"""

    controls: List[Control] = field(default_factory=list)
    """TODO: add docs"""

    # Controls

    def has_control(self, code: str):
        return bool(self.get_control(code))

    def get_control(
        self, code: str, *, ensure: Optional[Control] = None
    ) -> Optional[Control]:
        for control in self.controls:
            if control.code == code:
                return control
        if ensure:
            self.controls.append(ensure)
            return ensure

    # Metadata

    metadata_Error = errors.DialectError
    metadata_profile = {
        "type": "object",
        "required": [],
        "properties": {
            "headerRows": {},
            "headerJoin": {},
            "headerCase": {},
            "controls": {},
        },
    }


class Control(Metadata2):
    """Control representation"""

    code: str

    # Metadata

    metadata_Error = errors.ControlError
    metadata_defined = {"code"}
