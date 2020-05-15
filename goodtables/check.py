class Check(dict):
    def __init__(self, **context):
        self.update(context)
        self.__stream = None
        self.__schema = None

    @property
    def stream(self):
        return self.__stream

    @property
    def schema(self):
        return self.__schema

    @property
    def options(self):
        return self.__options

    # Validation

    def validate_start(self, *, stream, schema):
        self.__stream = stream
        self.__schema = schema
        return []

    def validate_headers(self, headers):
        return []

    def validate_row(self, row):
        return []

    def validate_finish(self):
        return []
