import datapackage
from .. import helpers
from ..task import Task
from ..report import Report
from ..errors import PackageError
from .resource import validate_resource


@Task.catch
def validate_package(source, strict=False, base_path=None, **options):
    timer = helpers.Timer()

    # Create package
    try:
        package = datapackage.Package(source, base_path=base_path)
    except datapackage.exceptions.DataPackageException as exception:
        time = timer.get_time()
        error = PackageError(details=str(exception))
        return Report(time=time, errors=[error], tables=[])

    # Package errors
    for stage in [1, 2]:
        errors = []
        if stage == 1:
            if not strict:
                continue
        if stage == 2:
            try:
                package.infer()
            except Exception as exception:
                errors.append(PackageError(details=str(exception)))
            for resource in list(package.resources):
                if not resource.tabular:
                    package.remove_resource(resource.name)
        for error in package.errors:
            errors.append(PackageError(details=str(error)))
        if errors:
            time = timer.get_time()
            return Report(time=time, errors=errors, tables=[])

    # Validate resources
    # TODO: make parallel
    reports = []
    for resource in package.resources:
        reports.append(
            validate_resource(
                resource.descriptor, strict=strict, base_path=package.base_path, **options
            )
        )

    # Return report
    time = timer.get_time()
    errors = []
    tables = []
    for report in reports:
        errors.extend(report['errors'])
        tables.extend(report['tables'])
    return Report(time=time, errors=errors, tables=tables)
