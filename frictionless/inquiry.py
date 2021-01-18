import stringcase
from .metadata import Metadata
from . import helpers
from . import errors
from . import config


# TODO: migrate run from validate_inquiry to here (sync with Pipeline)
class Inquiry(Metadata):
    """Inquiry representation.

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, tasks=None):
        self.setinitial("tasks", tasks)
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

    def metadata_process(self):

        # Tasks
        tasks = self.get("tasks")
        if isinstance(tasks, list):
            for index, task in enumerate(tasks):
                if not isinstance(task, InquiryTask):
                    task = InquiryTask(task)
                    list.__setitem__(tasks, index, task)
            if not isinstance(tasks, helpers.ControlledList):
                tasks = helpers.ControlledList(tasks)
                tasks.__onchange__(self.metadata_process)
                dict.__setitem__(self, "tasks", tasks)


class InquiryTask(Metadata):
    """Inquiry task representation.

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, source=None, type=None, **options):
        self.setinitial("source", source)
        self.setinitial("type", type)
        for key, value in options.items():
            # TODO: review
            self.setinitial(stringcase.camelcase(key), value)
        super().__init__(descriptor)

    @property
    def source(self):
        """
        Returns:
            any: source
        """
        return self["source"]

    @property
    def type(self):
        """
        Returns:
            string?: type
        """
        return self.get("type")

    # Metadata

    metadata_strict = True
    metadata_Error = errors.InquiryError
    metadata_profile = config.INQUIRY_PROFILE["properties"]["tasks"]["items"]
