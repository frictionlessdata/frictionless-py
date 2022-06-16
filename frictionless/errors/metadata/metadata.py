from ...error import Error


class MetadataError(Error):
    code = "metadata-error"
    name = "Metadata Error"
    template = "Metaata error: {note}"
    description = "There is a metadata error."
