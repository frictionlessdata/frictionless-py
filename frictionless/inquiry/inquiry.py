from copy import deepcopy
from typing import List
from ..metadata import Metadata
from ..errors import InquiryError
from .validate import validate
from .task import InquiryTask
from .. import settings


class Inquiry(Metadata):
    """Inquiry representation.

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    validate = validate

    def __init__(self, tasks: List[InquiryTask]):
        self.setinitial("tasks", tasks)
        super().__init__()

    @property
    def tasks(self):
        """
        Returns:
            dict[]: tasks
        """
        return self["tasks"]

    # Export/Import

    @staticmethod
    # TODO: recover after a cyclic dep is resolved
    #  def from_descriptor(descriptor: IDescriptor):
    def from_descriptor(descriptor: dict):
        metadata = Metadata(descriptor)
        tasks = [InquiryTask.from_descriptor(task) for task in metadata.get("tasks", [])]
        return Inquiry(tasks=tasks)

    # Metadata

    metadata_Error = InquiryError
    metadata_profile = deepcopy(settings.INQUIRY_PROFILE)
    metadata_profile["properties"]["tasks"] = {"type": "array"}

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Tasks
        for task in self.tasks:
            yield from task.metadata_errors
