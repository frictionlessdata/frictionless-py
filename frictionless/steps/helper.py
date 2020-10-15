import petl


class ResourceView(petl.Table):
    def __init__(self, resource):
        self.__resource = resource

    def __iter__(self):
        yield self.__resource.schema.field_names
        yield from self.__resource.read_data_stream()
