from ...error import Error


class MetadataError(Error):
    name = "Metadata Error"
    type = "metadata-error"
    template = "Metaata error: {note}"
    description = "There is a metadata error."
