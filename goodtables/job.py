from .metadata import Metadata
from . import config


class Job(Metadata):
    metadata_profile = config.JOB_PROFILE

    @property
    def tasks(self):
        return self['tasks']
