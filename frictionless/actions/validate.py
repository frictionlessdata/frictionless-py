from typing import Optional, List, Any, Union
from ..stats import Stats
from ..schema import Schema
from ..report import Report
from ..dialect import Dialect
from ..inquiry import Inquiry
from ..package import Package
from ..pipeline import Pipeline
from ..resource import Resource
from ..detector import Detector
from ..checklist import Checklist, Check
from ..exception import FrictionlessException
from .. import settings
from .. import helpers


def validate(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    dialect: Optional[Union[Dialect, str]] = None,
    schema: Optional[Union[Schema, str]] = None,
    stats: Optional[Stats] = None,
    # Checklist
    checklist: Optional[Union[Checklist, str]] = None,
    checks: List[Check] = [],
    pick_errors: List[str] = [],
    skip_errors: List[str] = [],
    # Validate
    resource_name: Optional[str] = None,
    limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    limit_rows: Optional[int] = None,
    parallel: bool = False,
    **options,
):
    """Validate resource

    Parameters:
        source (dict|str): a data source
        type (str): source type - inquiry, package, resource, schema or table
        **options (dict): options for the underlaying function

    Returns:
        Report: validation report
    """
    timer = helpers.Timer()

    # Detect type
    if resource_name:
        type = "resource"
    if not type:
        type = getattr(source, "metadata_type", None)
    if not type:
        type = Detector.detect_descriptor(source)
    if not type:
        type = "resource"
        if helpers.is_expandable_source(source):
            type = "package"

    # Create checklist
    if isinstance(checklist, str):
        checklist = Checklist.from_descriptor(checklist)
    elif not checklist:
        checklist = Checklist(
            checks=checks,
            pick_errors=pick_errors,
            skip_errors=skip_errors,
        )

    # Validate resource
    if type == "resource":
        try:
            if resource_name:
                package = source
                if not isinstance(package, Package):
                    package = Package.from_options(source, **options)
                resource = package.get_resource(resource_name)
            else:
                resource = source
                if not isinstance(resource, Resource):
                    resource = Resource.from_options(
                        source,
                        dialect=dialect,
                        schema=schema,
                        stats=stats,
                        **options,
                    )
        except FrictionlessException as exception:
            return Report.from_validation(time=timer.time, errors=exception.to_errors())
        return resource.validate(
            checklist,
            limit_errors=limit_errors,
            limit_rows=limit_rows,
        )

    # Validate package
    if type == "package":
        try:
            package = source
            if not isinstance(package, Package):
                package = Package.from_options(source, **options)
        except FrictionlessException as exception:
            return Report.from_validation(time=timer.time, errors=exception.to_errors())
        return package.validate(
            checklist,
            limit_errors=limit_errors,
            limit_rows=limit_rows,
            parallel=parallel,
        )

    # Ensure source
    if source is None:
        note = f'"source" is required for "{type}" validation'
        raise FrictionlessException(note)

    # Validate checklist
    if type == "checklist":
        return Checklist.validate_descriptor(source)

    # Validate detector
    if type == "detector":
        return Detector.validate_descriptor(source)

    # Validate dialect
    if type == "dialect":
        return Dialect.validate_descriptor(source)

    # Validate inquiry
    if type == "inquiry":
        try:
            inquiry = Inquiry.from_descriptor(source)
        except FrictionlessException as exception:
            return Report.from_validation(time=timer.time, errors=exception.to_errors())
        return inquiry.validate()

    # Validate pipeline
    if type == "pipeline":
        return Pipeline.validate_descriptor(source)

    # Validate report
    if type == "report":
        return Report.validate_descriptor(source)

    # Validate schema
    if type == "schema":
        return Schema.validate_descriptor(source)

    # Not supported
    raise FrictionlessException(f"Not supported validate type: {type}")
