from .config import SPEC, SPEC_PROFILE


class Spec(dict):
    def __init__(self):
        super().__init__(SPEC)
        self.__profile = SPEC_PROFILE
