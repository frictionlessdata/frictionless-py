from .metadata import Metadata
from . import errors
from . import config


class Inquiry(Metadata):
    """Inquiry representation.

    Parameters:
        descriptor? (str|dict): schema descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor):
        super().__init__(descriptor)

    @property
    def tasks(self):
        """
        Returns:
            dict[]: tasks
        """
        return self["tasks"]

    # Metadata

    metadata_strict = True
    metadata_Error = errors.InquiryError
    metadata_profile = config.INQUIRY_PROFILE
