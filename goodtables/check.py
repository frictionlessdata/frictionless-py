class Check:
    def __init__(self, *, stream, schema, **options):
        self.__schema = schema
        self.__options = options

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
