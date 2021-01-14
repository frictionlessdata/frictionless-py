from .metadata import Metadata
from . import errors
from . import config


# TODO: Add InquiryTask class?
# TODO: migrate run from validate_inquiry to here (sync with Pipeline)
# TODO: add system create_inquiry?
class Inquiry(Metadata):
    """Inquiry representation.

    Parameters:
        descriptor? (str|dict): schema descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

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
