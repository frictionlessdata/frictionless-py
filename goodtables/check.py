from .descriptor import Descriptor


class Check(Descriptor):
    def __init__(self, descriptor=None, **props):
        super().__init__(descriptor, **props)
        self.__stream = None
        self.__schema = None

    @property
    def stream(self):
        return self.__stream

    @property
    def schema(self):
        return self.__schema

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
