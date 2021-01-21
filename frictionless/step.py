from .metadata import Metadata
from . import errors


# TODO: finalize
class Step(Metadata):
    code = "step"

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.setinitial("code", self.code)

    def transorm_resource(self, source, target):
        pass

    def transorm_package(self, source, target):
        pass

    # Metadata

    metadata_strict = True
    metadata_Error = errors.StepError
