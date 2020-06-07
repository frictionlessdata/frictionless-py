from .metadata import Metadata
from . import config


class Inquiry(Metadata):
    metadata_profile = config.INQUIRY_PROFILE

    @property
    def tasks(self):
        return self['tasks']
