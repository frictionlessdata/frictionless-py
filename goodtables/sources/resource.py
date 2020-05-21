import datapackage
from .. import helpers
from ..report import Report
from ..errors import ResourceError, TaskError
from .table import validate_table


# TODO: support multipart paths
# https://github.com/frictionlessdata/datapackage-py/pull/257
def validate_resource(resource, strict=False, base_path=None, **options):
    timer = helpers.Timer()

    try:

        # Create resource
        try:
            resource = datapackage.Resource(resource, base_path=base_path)
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

        # Return report
        time = timer.get_time()
        return Report(time=time, errors=report['errors'], tables=report['tables'])

    except Exception as exception:

        # Prepare report
        time = timer.get_time()
        error = TaskError(details=str(exception))

        # Return report
        return Report(time=time, errors=[error], tables=[])
