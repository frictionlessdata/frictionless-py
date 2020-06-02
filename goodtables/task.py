import functools
from .metadata import Metadata
from .errors import TaskError
from .helpers import Timer
from .report import Report
from . import config


class Task(Metadata):
    metadata_profile = config.TASK_PROFILE

    # Helpers

    @staticmethod
    def catch(validate):
        @functools.wraps(validate)
        def wrapper(*args, **kwargs):
            timer = Timer()
            try:
                return validate(*args, **kwargs)
            except Exception as exception:
                time = timer.get_time()
                error = TaskError(details=str(exception))
                return Report(time=time, errors=[error], tables=[])

        return wrapper
