from .metadata import Metadata


class Step(Metadata):
    code = "step"

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.setinitial("code", self.code)
