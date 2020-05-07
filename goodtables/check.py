class Check:
    def __init__(self, spec, *, stream, schema, **options):
        self.__spec = spec
        self.__stream = stream
        self.__schema = schema
        self.__options = options

    @property
    def spec(self):
        return self.__spec

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

    def validate_start(self):
        return []

    def validate_table_headers(self, headers):
        return []

    def validate_table_row(self, row):
        return []

    def validate_finish(self):
        return []
