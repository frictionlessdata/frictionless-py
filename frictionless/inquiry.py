import stringcase
from functools import partial
from multiprocessing import Pool
from importlib import import_module
from .metadata import Metadata
from .exception import FrictionlessException
from .errors import InquiryError
from .system import system
from .report import Report
from . import helpers
from . import config


# TODO: move validation logic to validate_inquiry?
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

    # Run

    def run(self, *, parallel=False):
        validate = import_module("frictionless").validate

        # Create state
        tasks = []
        reports = []
        timer = helpers.Timer()

        # Prepare tasks
        for task in self.tasks:
            if task.type == "inquiry":
                note = "Inquiry cannot contain nested inquiries"
                raise FrictionlessException(InquiryError(note=note))
            if task.type == "package":
                # TODO:
                # For now, we don't flatten inquiry completely and for the case
                # of a list of packages with one resource we don't get proper multiprocessing
                report = validate(**helpers.create_options(task))
                reports.append(report)
                continue
            tasks.append(task)

        # Validate sequentially
        if len(tasks) == 1 or not parallel:
            for task in tasks:
                report = validate(**helpers.create_options(task))
                reports.append(report)

        # Validate in-parallel
        else:
            with Pool() as pool:
                reports.extend(pool.map(partial(helpers.apply_function, validate), tasks))

        # Return report
        errors = []
        tasks = []
        for report in reports:
            errors.extend(report["errors"])
            tasks.extend(report["tasks"])
        return Report(time=timer.time, errors=errors, tasks=tasks)

    # Metadata

    metadata_strict = True
    metadata_Error = InquiryError
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
        return self.get("type") or system.create_file(self.source).type

    # Metadata

    metadata_strict = True
    metadata_Error = InquiryError
    metadata_profile = config.INQUIRY_PROFILE["properties"]["tasks"]["items"]
