from .metadata import Metadata


class Check(Metadata):
    possible_Errors = []  # type: ignore

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__stream = None
        self.__schema = None

    @property
    def stream(self):
        return self.__stream

    @property
    def schema(self):
        return self.__schema

    # Validation

    def connect(self, *, stream, schema):
        self.__stream = stream
        self.__schema = schema

    def prepare(self):
        pass

    def validate_task(self):
        return []

    def validate_headers(self, headers):
        return []

    def validate_row(self, row):
        return []

    def validate_table(self):
        return []
