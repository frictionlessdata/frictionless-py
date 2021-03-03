from .metadata import Metadata


# NOTE:
# Consider other approaches for report/errors as dict is not really
# effective as it can be very memory consumig. As an option we can store
# raw data without rendering an error template to an error messsage.
# Also, validation is disabled for performance reasons at the moment.
# Allow creating from a descriptor (note needs to be optional)


class Error(Metadata):
    """Error representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import errors`

    Parameters:
        descriptor? (str|dict): error descriptor
        note (str): an error note

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    code = "error"
    name = "Error"
    tags = []  # type: ignore
    template = "{note}"
    description = "Error"

    def __init__(self, descriptor=None, *, note):
        super().__init__(descriptor)
        self.setinitial("code", self.code)
        self.setinitial("name", self.name)
        self.setinitial("tags", self.tags)
        self.setinitial("note", note)
        self.setinitial("message", self.template.format(**self))
        self.setinitial("description", self.description)

    @property
    def note(self):
        """
        Returns:
            str: note
        """
        return self["note"]

    @property
    def message(self):
        """
        Returns:
            str: message
        """
        return self["message"]
