from .metadata import Metadata
from . import config


class Query(Metadata):
    metadata_profile = config.QUERY_PROFILE

    @property
    def tasks(self):
        return self['tasks']
