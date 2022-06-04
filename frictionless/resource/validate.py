import types
from typing import TYPE_CHECKING, List, Union, Optional
from ..check import Check
from ..system import system
from ..checklist import Checklist
from ..exception import FrictionlessException
from ..errors import GeneralError, TaskError
from ..report import Report, ReportTask
from .. import settings
from .. import helpers

if TYPE_CHECKING:
    from ..interfaces import CheckFunction
    from .resource import Resource


def validate(
    resource: "Resource",
    checklist: Optional[Checklist] = None,
    *,
    checks: Optional[List[Union[Check, CheckFunction]]] = None,
):
    """Validate resource

    Parameters:
        checklist? (checklist): a Checklist object
        checks? (list): a list of checks

    Returns:
        Report: validation report
    """

    # Create state
    partial = False
    timer = helpers.Timer()
    original_resource = resource.to_copy()

    # Prepare checklist
    if not checklist:
        if not checks:
            note = "checklist OR checks are required"
            raise FrictionlessException(GeneralError(note=note))
        proc = lambda check: check if isinstance(check, Check) else Check(function=check)
        checklist = Checklist(checks=list(map(proc, checks)))

    # Validate checklist
    if not checklist.metadata_valid:
        note = f"checklist is not valid: {checklist.metadata_errors[0]}"
        raise FrictionlessException(GeneralError(note=note))

    # Prepare check/errors
    checks = checklist.connect(resource)
    errors = ManagedErrors(checklist)
    for check in checklist.checks:
        errors.register(check)

    # Prepare resource
    try:
        resource.open()
    except FrictionlessException as exception:
        errors.append(exception.error)
        resource.close()

    # Validate metadata
    if not errors:
        metadata_resource = original_resource if checklist.original else resource
        for error in metadata_resource.metadata_errors:
            errors.append(error)

    # Validate data
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


def create_report(resource: Resource, *, partial, errors, time):
    return Report(
        time=time,
        errors=[],
        tasks=[
            ReportTask(
                time=time,
                scope=errors.scope,
                partial=partial,
                errors=errors,
                resource=resource,
            )
        ],
    )


# TODO: consider merging some logic into Checklist
class ManagedErrors(list):
    def __init__(self, checklist):
        self.__pick_errors = set(checklist.pick_errors)
        self.__skip_errors = set(checklist.skip_errors)
        self.__limit_errors = checklist.limit_errors
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
