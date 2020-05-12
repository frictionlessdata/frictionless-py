import tabulator
from copy import deepcopy
from .config import SPEC, SPEC_PROFILE
from .error import Error


class Spec(dict):
    def __init__(self):
        super().__init__(deepcopy(SPEC))
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

    def create_error_from_exception(self, exception):
        code = 'source-error'
        details = str(exception)
        if isinstance(exception, tabulator.exceptions.IOError):
            code = 'loading-error'
        if isinstance(exception, tabulator.exceptions.SourceError):
            code = 'source-error'
        if isinstance(exception, tabulator.exceptions.SchemeError):
            code = 'scheme-error'
        if isinstance(exception, tabulator.exceptions.FormatError):
            code = 'format-error'
        if isinstance(exception, tabulator.exceptions.EncodingError):
            code = 'encoding-error'
        return Error(code, context={'details': details})
