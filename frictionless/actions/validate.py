import types
import inspect
import warnings
from ..check import Check
from ..schema import Schema
from ..package import Package
from ..inquiry import Inquiry, InquiryTask
from ..system import system
from ..resource import Resource
from ..report import Report, ReportTask
from ..errors import TaskError
from ..exception import FrictionlessException
from .. import helpers
from .. import settings
from .. import errors


@Report.from_validate
def validate(source=None, type=None, **options):
    """Validate resource

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate`

    Parameters:
        source (dict|str): a data source
        type (str): source type - inquiry, package, resource, schema or table
        **options (dict): options for the underlaying function

    Returns:
        Report: validation report
    """
    if not type:
        basepath = options.get("basepath", "")
        descriptor = options.get("descriptor")
        file = system.create_file(descriptor or source, basepath=basepath)
        type = "package" if file.multipart else file.type
        if type == "table":
            type = "resource"
    validate = globals().get("validate_%s" % type, None)
    if validate is None:
        note = f"Not supported validate type: {type}"
        raise FrictionlessException(errors.GeneralError(note=note))
    # NOTE:
    # Review whether it's a proper place for this (program sends a detector)
    # We might resolve it when we convert Detector to be a metadata
    if type in ["inquiry", "schema"]:
        options.pop("detector", None)
    if type != "package":
        options.pop("resource_name", None)
    return validate(source, deprecate=False, **options)


@Report.from_validate
def validate_inquiry(source=None, *, parallel=False, deprecate=True, **options):
    """Validate inquiry

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_inquiry`

    Parameters:
        source (dict|str): an inquiry descriptor
        parallel? (bool): enable multiprocessing

    Returns:
        Report: validation report

    """
    if deprecate:
        message = 'Function "validate_inquiry" is deprecated (use "inquiry.validate").'
        warnings.warn(message, UserWarning)
    native = isinstance(source, Inquiry)
    inquiry = source.to_copy() if native else Inquiry(source, **options)
    return inquiry.run(parallel=parallel)


@Report.from_validate
def validate_package(
    source=None, original=False, parallel=False, deprecate=True, **options
):
    """Validate package

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_package`

    Parameters:
        source (dict|str): a package descriptor
        basepath? (str): package basepath
        trusted? (bool): don't raise an exception on unsafe paths
        original? (bool): validate metadata as it is (without inferring)
        parallel? (bool): enable multiprocessing
        **options (dict): Package constructor options

    Returns:
        Report: validation report

    """
    if deprecate:
        message = 'Function "validate_package" is deprecated (use "package.validate").'
        warnings.warn(message, UserWarning)

    # Create state
    timer = helpers.Timer()

    # Prepare options
    package_options = {}
    signature = inspect.signature(validate_resource)
    for name, value in options.copy().items():
        # Exclude resource_name from package_options
        if name == "resource_name":
            continue
        param = signature.parameters.get(name)
        if not param or param.kind != param.KEYWORD_ONLY:
            package_options[name] = options.pop(name)

    # Create package
    try:
        native = isinstance(source, Package)
        package = source.to_copy() if native else Package(source, **package_options)
        # For single resource validation
        if "resource_name" in options:
            return validate_resource(
                package.get_resource(options["resource_name"]), deprecate=False
            )
        package_stats = []
        for resource in package.resources:
            package_stats.append({key: val for key, val in resource.stats.items() if val})
    except FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tasks=[])

    # Validate metadata
    metadata_errors = []
    for error in package.metadata_errors:
        if error.code == "package-error":
            metadata_errors.append(error)
        if metadata_errors:
            return Report(time=timer.time, errors=metadata_errors, tasks=[])

    # Validate sequentially
    if not parallel:
        tasks = []
        errors = []
        for resource, stats in zip(package.resources, package_stats):
            resource.stats = stats
            report = validate_resource(
                resource, original=original, deprecate=False, **options
            )
            tasks.extend(report.tasks)
            errors.extend(report.errors)
        return Report(time=timer.time, errors=errors, tasks=tasks)

    # Validate in-parallel
    else:
        inquiry = Inquiry(tasks=[])
        for resource, stats in zip(package.resources, package_stats):
            for fk in resource.schema.foreign_keys:
                if fk["reference"]["resource"]:
                    message = "Foreign keys validation is ignored in the parallel mode"
                    warnings.warn(message, UserWarning)
                    break
            resource.stats = stats
            inquiry.tasks.append(
                InquiryTask(
                    source=resource,
                    basepath=resource.basepath,
                    original=original,
                    **options,
                )
            )
        return inquiry.run(parallel=parallel)


# NOTE:
# Shall metadata validation be a part of BaselineCheck?


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
    deprecate=True,
    # We ignore this line because of a problem with `make docs`:
    # https://github.com/frictionlessdata/frictionless-py/issues/1031
    # fmt: off
    **options
    # fmt: on
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
        original? (bool): validate metadata as it is (without inferring)
        **options? (dict): Resource constructor options

    Returns:
        Report: validation report
    """
    if deprecate:
        message = 'Function "validate_resource" is deprecated (use "resource.validate").'
        warnings.warn(message, UserWarning)

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
        original_resource = resource.to_copy()
    except FrictionlessException as exception:
        errors.append(exception.error)

    # Open resource
    if not errors:
        try:
            resource.open()
        except FrictionlessException as exception:
            errors.append(exception.error)
            resource.close()

    # Prepare checks
    if not errors:
        checks = checks.copy() if checks else []
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

    # Validate metadata
    if not errors:
        metadata_resource = original_resource if original else resource
        for error in metadata_resource.metadata_errors:
            errors.append(error)

    # Validate data
    if not errors:
        with resource:
            # Validate start
            indices_of_checks_to_remove = []
            for index, check in enumerate(checks):
                check.connect(resource)
                for error in check.validate_start():
                    if error.code == "check-error":
                        indices_of_checks_to_remove.append(index)
                    errors.append(error)
            checks = [
                check
                for i, check in enumerate(checks)
                if i not in indices_of_checks_to_remove
            ]

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


@Report.from_validate
def validate_schema(source=None, deprecate=True, **options):
    """Validate schema

    API      | Usage
    -------- | --------
    Public   | `from frictionless import validate_schema`

    Parameters:
        source (dict|str): a schema descriptor

    Returns:
        Report: validation report

    """
    if deprecate:
        message = 'Function "validate_schema" is deprecated (use "schema.validate").'
        warnings.warn(message, UserWarning)

    # Create state
    timer = helpers.Timer()

    # Create schema
    try:
        native = isinstance(source, Schema)
        schema = source.to_copy() if native else Schema(source, **options)
    except FrictionlessException as exception:
        return Report(time=timer.time, errors=[exception.error], tasks=[])

    # Return report
    return Report(time=timer.time, errors=schema.metadata_errors, tasks=[])


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
