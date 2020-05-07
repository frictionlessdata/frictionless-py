from copy import deepcopy
from .config import SPEC, SPEC_PROFILE
from .error import Error


class Spec(dict):
    def __init__(self, spec=SPEC):
        super().__init__(spec)
        # TODO: validate
        SPEC_PROFILE

    def create_error(self, code, *, context):
        # TODO: handle key errors
        error = deepcopy(self[code])
        # TODO: handle formatting errors
        error['message'] = error['message'].format(**context)
        # TODO: validate the context according to the spec
        error['context'] = context
        return Error(**error)
