from copy import deepcopy
from .config import SPEC, SPEC_PROFILE


class Spec(dict):
    def __init__(self, spec=SPEC):
        super().__init__(deepcopy(spec))

    def validate(self):
        print(SPEC_PROFILE)
