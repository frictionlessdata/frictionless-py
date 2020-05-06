from copy import deepcopy
from .config import SPEC, SPEC_PROFILE


class Spec(dict):
    def __init__(self, spec=SPEC):
        super().__init__(deepcopy(spec))
        # TODO: validate
        SPEC_PROFILE
