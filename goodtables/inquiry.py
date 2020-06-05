from .metadata import Metadata
from . import config


class Inquiry(Metadata):
    metadata_profile = config.INQUIRY_PROFILE

    @property
    def sources(self):
        return self['sources']
