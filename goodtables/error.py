from copy import deepcopy


class Error(dict):
    def __init__(self, code, *, name, message, description, tags, context):
        self['code'] = code
        self['name'] = name
        self['description'] = description
        self['tags'] = tags
        self['context'] = context

    @classmethod
    def fromSpec(cls, spec, code, context):
        # TODO: handle key errors
        error = deepcopy(spec[code])
        # TODO: handle formatting errors
        error['message'] = error['message'].format(**context)
        # TODO: validate the context according to the spec
        error['context'] = context
        return cls(**error)
