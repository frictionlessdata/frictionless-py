import datapackage
from .. import helpers
from ..report import Report
from ..inquiry import Inquiry
from ..errors import PackageError
from .inquiry import validate_inquiry


@Report.catch
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

    # Validate inquiry
    descriptor = {'sources': []}
    for resource in package.resources:
        source = {}
        source['source'] = resource.source
        source['strict'] = strict
        source['basePath'] = base_path
        source.update(helpers.create_descriptor_from_options(options))
        descriptor['sources'].append(source)
    report = validate_inquiry(Inquiry(descriptor))

    # Return report
    time = timer.get_time()
    return Report(time=time, errors=report['errors'], tables=report['tables'])
