from typing import Optional, List, Any
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


# TODO: shall we accept dialect/schema/checklist in a form of descriptors?
def validate(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    # Checklist
    checklist: Optional[Checklist] = None,
    checks: List[Check] = [],
    pick_errors: List[str] = [],
    skip_errors: List[str] = [],
    # Validate
    resource_name: Optional[str] = None,
    limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    limit_rows: Optional[int] = None,
    parallel: bool = False,
    strict: bool = False,
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

    # Detect type
    if not type:
        type = Detector.detect_descriptor(source)
        if not type:
            type = "resource"
            if helpers.is_expandable_source(source):
                type = "package"

    # Create checklist
    if not checklist:
        checklist = Checklist(
            checks=checks,
            pick_errors=pick_errors,
            skip_errors=skip_errors,
        )

    # Validate resource
    if type == "resource":
        resource = Resource.from_options(source, **options)
        return resource.validate(
            checklist,
            limit_errors=limit_errors,
            limit_rows=limit_rows,
            strict=strict,
        )

    # Validate package
    if type == "package":
        # TODO: remove when we add these to names kwargs
        options.pop("schema", None)
        options.pop("dialect", None)
        options.pop("checklist", None)
        options.pop("pipeline", None)
        options.pop("stats", None)
        package = Package.from_options(source, **options)

        # Resource
        if resource_name:
            resource = package.get_resource(resource_name)
            return resource.validate(
                checklist,
                limit_errors=limit_errors,
                limit_rows=limit_rows,
                strict=strict,
            )

        # Package
        else:
            return package.validate(
                checklist,
                limit_errors=limit_errors,
                limit_rows=limit_rows,
                strict=strict,
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
        inquiry = Inquiry.from_descriptor(source)
        return inquiry.validate()

    # Validate pipeline
    if type == "pipeline":
        pipeline = Pipeline.from_descriptor(source)
        return pipeline.validate()

    # Validate report
    if type == "report":
        return Report.validate_descriptor(source)

    # Validate schema
    if type == "schema":
        return Schema.validate_descriptor(source)

    # Not supported
    raise FrictionlessException(f"Not supported validate type: {type}")
