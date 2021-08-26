import stringcase
from copy import deepcopy
from multiprocessing import Pool
from importlib import import_module
from .metadata import Metadata
from .errors import InquiryError
from .system import system
from .report import Report
from . import settings
from . import helpers


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

        # Create state
        reports = []
        timer = helpers.Timer()

        # Validate inquiry
        if self.metadata_errors:
            return Report(time=timer.time, errors=self.metadata_errors, tasks=[])

        # Validate sequentially
        if not parallel:
            for task in self.tasks:
                report = task.run()
                reports.append(report)

        # Validate in-parallel
        else:
            with Pool() as pool:
                task_descriptors = [task.to_dict() for task in self.tasks]
                report_descriptors = pool.map(run_task_in_parallel, task_descriptors)
                for report_descriptor in report_descriptors:
                    reports.append(Report(report_descriptor))

        # Return report
        tasks = []
        errors = []
        for report in reports:
            tasks.extend(report.tasks)
            errors.extend(report.errors)
        return Report(time=timer.time, errors=errors, tasks=tasks)

    # Metadata

    metadata_Error = InquiryError
    metadata_profile = deepcopy(settings.INQUIRY_PROFILE)
    metadata_profile["properties"]["tasks"] = {"type": "array"}

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

    def metadata_validate(self):
        yield from super().metadata_validate()

        # Tasks
        for task in self.tasks:
            yield from task.metadata_errors


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

    # Run

    def run(self):
        validate = import_module("frictionless").validate
        report = validate(**helpers.create_options(self))
        return report

    # Metadata

    metadata_Error = InquiryError
    metadata_profile = settings.INQUIRY_PROFILE["properties"]["tasks"]["items"]


# Internal


def run_task_in_parallel(task_descriptor):
    task = InquiryTask(task_descriptor)
    report = task.run()
    report_descriptor = report.to_dict()
    return report_descriptor
