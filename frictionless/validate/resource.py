import types
from ..check import Check
from ..system import system
from ..resource import Resource
from ..exception import FrictionlessException
from ..report import Report, ReportTask
from .. import config
from .. import errors
from .. import helpers


@Report.from_validate
def validate_resource(
    source,
    *,
    # Validation
    checks=None,
    pick_errors=None,
    skip_errors=None,
    limit_errors=config.DEFAULT_LIMIT_ERRORS,
    limit_memory=config.DEFAULT_LIMIT_MEMORY,
    original=False,
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
    partial = False
    task_errors = []
    resource_errors = ResourceErrors(pick_errors, skip_errors, limit_errors)
    timer = helpers.Timer()

    # Create resource
    try:
        native = isinstance(source, Resource)
        resource = source.to_copy() if native else Resource(source, **options)
    except FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tasks=[])

    # Prepare stats
    stats = {}
    if resource.stats:
        stats = {key: val for key, val in resource.stats.items() if val}

    # Prepare resource
    if not original:
        resource.infer()
    if resource.metadata_errors:
        return Report(time=timer.time, errors=resource.metadata_errors, tasks=[])

    # Open resource
    try:
        resource.open()
    except FrictionlessException as exception:
        resource_errors.append(exception.error, force=True)
        resource.close()

    # Prepare checks
    checks = checks or []
    checks.insert(0, {"code": "baseline", "stats": stats})
    for index, check in enumerate(checks):
        if not isinstance(check, Check):
            checks[index] = (
                Check(function=check)
                if isinstance(check, types.FunctionType)
                else system.create_check(check)
            )

    # Validate checks
    for index, check in enumerate(checks.copy()):
        if check.metadata_errors:
            task_errors.extend(check.metadata_errors)
            del check[index]

    # Enter table
    if not resource_errors:
        with resource:

            # Prepare checks
            for check in checks:
                resource_errors.register(check)
                check.connect(resource)
                check.prepare()

            # Validate checks
            for check in checks.copy():
                for error in check.validate_check():
                    task_errors.append(error)
                    if check in checks:
                        checks.remove(check)

            # Validate source
            for check in checks:
                for error in check.validate_source():
                    resource_errors.append(error, force=True)

            # Validate schema
            for check in checks:
                for error in check.validate_schema():
                    resource_errors.append(error, force=True)

            # Validate header
            if resource.header:
                for check in checks:
                    for error in check.validate_header():
                        resource_errors.append(error)

            # Validate rows
            for row in resource.row_stream:

                # Validate row
                for check in checks:
                    for error in check.validate_row(row):
                        resource_errors.append(error)

                # Limit errors
                if limit_errors and len(resource_errors) >= limit_errors:
                    partial = True
                    break

                # Limit memory
                if limit_memory and not resource.stats["rows"] % 100000:
                    memory = helpers.get_current_memory_usage()
                    if memory and memory > limit_memory:
                        note = f'exceeded memory limit "{limit_memory}MB"'
                        task_errors.append(errors.TaskError(note=note))
                        partial = True
                        break

            # Validate table
            if not partial:
                for check in checks:
                    for error in check.validate_table():
                        resource_errors.append(error)

    # Return report
    return Report(
        time=timer.time,
        errors=task_errors,
        tasks=[
            ReportTask(
                time=timer.time,
                scope=resource_errors.scope,
                partial=partial,
                errors=resource_errors,
                resource=resource,
            )
        ],
    )


# Internal


class ResourceErrors(list):
    def __init__(self, pick_errors, skip_errors, limit_errors):
        self.__pick_errors = set(pick_errors or [])
        self.__skip_errors = set(skip_errors or [])
        self.__limit_errors = limit_errors
        self.__scope = []

    @property
    def scope(self):
        return self.__scope

    def append(self, error, *, force=False):
        if not force:
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
