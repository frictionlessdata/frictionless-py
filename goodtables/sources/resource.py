import stringcase
import datapackage
from .. import helpers
from ..task import task
from ..report import Report
from ..errors import ResourceError
from .table import validate_table


@task
def validate_resource(source, strict=False, base_path=None, **options):
    timer = helpers.Timer()

    # Create resource
    try:
        resource = datapackage.Resource(source, base_path=base_path)
    except datapackage.exceptions.DataPackageException as exception:
        time = timer.get_time()
        error = ResourceError(details=str(exception))
        return Report(time=time, errors=[error], tables=[])

    # Resource errors
    for stage in [1, 2]:
        errors = []
        if stage == 1:
            if not strict:
                continue
        if stage == 2:
            try:
                resource.infer()
            except Exception as exception:
                errors.append(ResourceError(details=str(exception)))
        if not resource.tabular:
            errors.append(ResourceError(details='resource is not tabular'))
        for error in resource.errors:
            errors.append(ResourceError(details=str(error)))
        if errors:
            time = timer.get_time()
            return Report(time=time, errors=errors, tables=[])

    # Prepare dialect/headers
    headers_row = 1
    dialect = resource.descriptor.get('dialect', {})
    dialect = {stringcase.snakecase(key): value for key, value in dialect.items()}
    if dialect.get('header') is False:
        headers_row = None

    # Validate table
    report = validate_table(
        resource.source,
        scheme=resource.descriptor.get('scheme'),
        format=resource.descriptor.get('format'),
        encoding=resource.descriptor.get('encoding'),
        compression=resource.descriptor.get('compression'),
        headers_row=headers_row,
        pick_fields=resource.descriptor.get('pickFields'),
        skip_fields=resource.descriptor.get('skipFields'),
        limit_fields=resource.descriptor.get('limitFields'),
        offset_fields=resource.descriptor.get('offsetFields'),
        pick_rows=resource.descriptor.get('pickRows'),
        skip_rows=resource.descriptor.get('skipRows'),
        limit_rows=resource.descriptor.get('limitRows'),
        offset_rows=resource.descriptor.get('offsetRows'),
        size=resource.descriptor.get('bytes'),
        hash=resource.descriptor.get('hash'),
        schema=resource.descriptor.get('schema'),
        **options,
        **dialect,
    )

    # Return report
    time = timer.get_time()
    return Report(time=time, errors=report['errors'], tables=report['tables'])
