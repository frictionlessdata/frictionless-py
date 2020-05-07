class Error(dict):
    def __init__(self, code, *, name, message, description, tags, context):
        self['code'] = code
        self['name'] = name
        self['message'] = message
        self['description'] = description
        self['tags'] = tags
        self['context'] = context
