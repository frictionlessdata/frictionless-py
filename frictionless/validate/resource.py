import types
from ..check import Check
from ..system import system
from ..resource import Resource
from ..exception import FrictionlessException
from ..report import Report, ReportTask
from ..errors import TaskError
from .. import helpers
from .. import settings


@Report.from_validate
def validate_resource(
    source=None,
    *,
    # Validation
    checks=None,
    original=False,
    pick_errors=None,
    skip_errors=None,
    limit_errors=settings.DEFAULT_LIMIT_ERRORS,
    limit_memory=settings.DEFAULT_LIMIT_MEMORY,
    **options,
):
    """Validate table

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_table`

    Parameters:
        source (any): the source of the resource
        checks? (list): a list of checks
        pick_errors? ((str|int)[]): pick errors
        skip_errors? ((str|int)[]): skip errors
        limit_errors? (int): limit errors
        limit_memory? (int): limit memory
        original? (bool): validate resource as it is
        **options? (dict): Resource constructor options

    Returns:
        Report: validation report
    """

    # Create state
    resource = None
    partial = False
    timer = helpers.Timer()
    errors = ManagedErrors(pick_errors, skip_errors, limit_errors)

    # Create resource
    try:
        native = isinstance(source, Resource)
        resource = source.to_copy() if native else Resource(source, **options)
        stats = {key: val for key, val in resource.stats.items() if val}
    except FrictionlessException as exception:
        errors.append(exception.error)

    # Prepare resource
    if not errors:
        if not original:
            resource.infer()
        if resource.metadata_errors:
            for error in resource.metadata_errors:
                errors.append(error)

    # Open resource
    if not errors:
        try:
            resource.open()
        except FrictionlessException as exception:
            errors.append(exception.error)
            resource.close()

    # Prepare checks
    if not errors:
        checks = checks or []
        checks.insert(0, {"code": "baseline", "stats": stats})
        for index, check in enumerate(checks):
            if not isinstance(check, Check):
                func = isinstance(check, types.FunctionType)
                check = Check(function=check) if func else system.create_check(check)
                checks[index] = check
            errors.register(check)

    # Validate checks
    if not errors:
        for index, check in enumerate(checks.copy()):
            if check.metadata_errors:
                del checks[index]
                for error in check.metadata_errors:
                    errors.append(error)

    # Validate resource
    if not errors:
        with resource:

            # Validate start
            for index, check in enumerate(checks.copy()):
                check.connect(resource)
                for error in check.validate_start():
                    if error.code == "check-error":
                        del checks[index]
                    errors.append(error)

            # Validate rows
            if resource.tabular:
                for row in resource.row_stream:

                    # Validate row
                    for check in checks:
                        for error in check.validate_row(row):
                            errors.append(error)

                    # Limit errors
                    if limit_errors and len(errors) >= limit_errors:
                        partial = True
                        break

                    # Limit memory
                    if limit_memory and not row.row_number % 100000:
                        memory = helpers.get_current_memory_usage()
                        if memory and memory > limit_memory:
                            note = f'exceeded memory limit "{limit_memory}MB"'
                            errors.append(TaskError(note=note))
                            partial = True
                            break

            # Validate end
            if not partial:
                if not resource.tabular:
                    helpers.pass_through(resource.byte_stream)
                for check in checks:
                    for error in check.validate_end():
                        errors.append(error)

    # Return report
    return Report(
        time=timer.time,
        errors=[],
        tasks=[
            ReportTask(
                time=timer.time,
                scope=errors.scope,
                partial=partial,
                errors=errors,
                resource=resource,
            )
        ],
    )


# Internal


# NOTE:
# We might consider merging this code into ReportTask
# It had been written much earlier that ReportTask was introduces
# Also, we can use Report/ReportTask API instead of working with lists


class ManagedErrors(list):
    def __init__(self, pick_errors, skip_errors, limit_errors):
        self.__pick_errors = set(pick_errors or [])
        self.__skip_errors = set(skip_errors or [])
        self.__limit_errors = limit_errors
        self.__scope = []

    @property
    def scope(self):
        return self.__scope

    def append(self, error):
        if "#general" not in error.tags:
            if self.__limit_errors:
                if len(self) >= self.__limit_errors:
                    return
            if not self.match(error):
                return
        super().append(error)

    def match(self, error):
        match = True
        if self.__pick_errors:
            match = False
            if error.code in self.__pick_errors:
                match = True
            if self.__pick_errors.intersection(error.tags):
                match = True
        if self.__skip_errors:
            match = True
            if error.code in self.__skip_errors:
                match = False
            if self.__skip_errors.intersection(error.tags):
                match = False
        return match

    def register(self, check):
        for Error in check.Errors:
            if not self.match(Error):
                continue
            if Error.code in self.__scope:
                continue
            self.__scope.append(Error.code)
