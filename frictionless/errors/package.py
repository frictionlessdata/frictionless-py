from ..error import Error


class PackageError(Error):
    code = "package-error"
    name = "Package Error"
    template = "The data package has an error: {note}"
    description = "A validation cannot be processed."
