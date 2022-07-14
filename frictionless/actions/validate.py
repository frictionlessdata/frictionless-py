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
    source: Any,
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

    # Validate package
    if type == "package":
        package = source
        if not isinstance(package, Package):
            # TODO: remove when we add these to names kwargs
            options.pop("schema", None)
            options.pop("dialect", None)
            options.pop("checklist", None)
            options.pop("pipeline", None)
            options.pop("stats", None)
            package = Package.from_options(package, **options)

        # Resource
        if resource_name:
            type = "resource"
            source = package.get_resource(resource_name)

        # Package
        else:
            return package.validate(
                checklist,
                limit_errors=limit_errors,
                limit_rows=limit_rows,
                strict=strict,
                parallel=parallel,
            )

    # Validate checklist
    if type == "checklist":
        checklist = source
        if not isinstance(checklist, Checklist):
            checklist = Checklist.from_descriptor(checklist)  # type: ignore
        return checklist.validate()

    # Validate detector
    elif type == "detector":
        detector = source
        if not isinstance(detector, Detector):
            detector = Detector.from_descriptor(detector)
        return detector.validate()

    # Validate dialect
    elif type == "dialect":
        dialect = source
        if not isinstance(dialect, Dialect):
            dialect = Dialect.from_descriptor(dialect)
        return dialect.validate()

    # Validate inquiry
    elif type == "inquiry":
        inquiry = source
        if not isinstance(inquiry, Inquiry):
            inquiry = Inquiry.from_descriptor(inquiry)
        return inquiry.validate()

    # Validate pipeline
    elif type == "pipeline":
        pipeline = source
        if not isinstance(pipeline, Pipeline):
            pipeline = Pipeline.from_descriptor(pipeline)
        return pipeline.validate()

    # Validate report
    elif type == "report":
        report = source
        if not isinstance(report, Report):
            report = Report.from_descriptor(report)
        return report.validate()

    # Validate resource
    elif type == "resource":
        resource = source
        if not isinstance(resource, Resource):
            resource = Resource.from_options(resource, **options)
        return resource.validate(
            checklist,
            limit_errors=limit_errors,
            limit_rows=limit_rows,
            strict=strict,
        )

    # Validate schema
    elif type == "schema":
        schema = source
        if not isinstance(schema, Schema):
            schema = Schema.from_descriptor(schema)
        return schema.validate()

    # Not supported
    raise FrictionlessException(f"Not supported validate type: {type}")
