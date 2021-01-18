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
    checksum=None,
    extra_checks=None,
    pick_errors=None,
    skip_errors=None,
    limit_errors=config.DEFAULT_LIMIT_ERRORS,
    limit_memory=config.DEFAULT_LIMIT_MEMORY,
    noinfer=False,
    **options,
):
    """Validate table

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_table`

    Parameters:
        source (any): the source of the resource
        checksum? (dict): a checksum dictionary
        extra_checks? (list): a list of extra checks
        pick_errors? ((str|int)[]): pick errors
        skip_errors? ((str|int)[]): skip errors
        limit_errors? (int): limit errors
        limit_memory? (int): limit memory
        noinfer? (bool): validate resource as it is
        **options? (dict): Resource constructor options

    Returns:
        Report: validation report
    """

    # Create state
    checks = []
    partial = False
    task_errors = []
    table_errors = TableErrors(pick_errors, skip_errors, limit_errors)
    timer = helpers.Timer()

    # Create checks
    items = []
    items.append("baseline")
    items.append(("checksum", checksum))
    items.extend(extra_checks or [])
    create = system.create_check
    for item in items:
        p1, p2 = item if isinstance(item, (tuple, list)) else (item, None)
        check = p1(p2) if isinstance(p1, type) else create(p1, descriptor=p2)
        checks.append(check)

    # Create resource
    try:
        native = isinstance(source, Resource)
        resource = source.to_copy() if native else Resource(source, **options)
    except FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tasks=[])

    # Prepare resource
    if not noinfer:
        resource.infer()
    if resource.metadata_errors:
        return Report(time=timer.time, errors=resource.metadata_errors, tasks=[])

    # Open resource
    try:
        resource.open()
    except FrictionlessException as exception:
        table_errors.append(exception.error, force=True)
        resource.close()

    # Enter table
    if not table_errors:
        with resource:

            # Prepare checks
            for check in checks:
                table_errors.register(check)
                check.connect(resource)
                check.prepare()

            # Validate task
            for check in checks.copy():
                for error in check.validate_task():
                    task_errors.append(error)
                    if check in checks:
                        checks.remove(check)

            # Validate schema
            for check in checks:
                for error in check.validate_schema(resource.schema):
                    table_errors.append(error)

            # Validate header
            if resource.header:
                for check in checks:
                    for error in check.validate_header(resource.header):
                        table_errors.append(error)

            # Validate rows
            for row in resource.row_stream:

                # Validate row
                for check in checks:
                    for error in check.validate_row(row):
                        table_errors.append(error)

                # Limit errors
                if limit_errors and len(table_errors) >= limit_errors:
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
                        table_errors.append(error)

    # Return report
    return Report(
        time=timer.time,
        errors=task_errors,
        tasks=[
            ReportTask(
                time=timer.time,
                scope=table_errors.scope,
                partial=partial,
                errors=table_errors,
                resource=resource,
            )
        ],
    )


# Internal


class TableErrors(list):
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
        for error in check.possible_Errors:
            if not self.match(error):
                continue
            if error.code in self.__scope:
                continue
            self.__scope.append(error.code)
