import datapackage
from .. import helpers
from ..report import Report
from ..errors import ResourceError, TaskError
from .table import validate_table


# TODO: support multipart paths
# https://github.com/frictionlessdata/datapackage-py/pull/257
def validate_resource(resource, base_path=None, **options):
    timer = helpers.Timer()

    try:

        # Create resource
        resource = datapackage.Resource(resource, base_path=base_path)
        resource.infer()

        # Resource errors
        errors = []
        for error in resource.errors:
            errors.append(ResourceError(details=str(error)))
        if errors:
            time = timer.get_time()
            return Report(time=time, errors=errors, tables=[])

        # Prepare dialect/headers
        headers = 1
        dialect = resource.descriptor.get('dialect', {})
        if dialect.get('header') is False:
            headers = None

        # Validate table
        report = validate_table(
            resource.source,
            headers=headers,
            scheme=resource.descriptor.get('scheme'),
            format=resource.descriptor.get('format'),
            encoding=resource.descriptor.get('encoding'),
            compression=resource.descriptor.get('compression'),
            pick_fields=resource.descriptor.get('pickFields'),
            skip_fields=resource.descriptor.get('skipFields'),
            pick_rows=resource.descriptor.get('pickRows'),
            skip_rows=resource.descriptor.get('skipRows'),
            size=resource.descriptor.get('bytes'),
            hash=resource.descriptor.get('hash'),
            schema=resource.descriptor.get('schema'),
            **options,
            **dialect,
        )

        # Update/return report
        report['time'] = timer.get_time()
        return report

    except Exception as exception:

        # Prepare report
        time = timer.get_time()
        error = TaskError(details=str(exception))

        # Return report
        return Report(time=time, errors=[error], tables=[])
