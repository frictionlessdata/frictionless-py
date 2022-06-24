from typing import Optional, List, Any
from ..system import system
from ..check import Check
from ..schema import Schema
from ..report import Report
from ..dialect import Dialect
from ..inquiry import Inquiry
from ..package import Package
from ..pipeline import Pipeline
from ..resource import Resource
from ..detector import Detector
from ..checklist import Checklist
from ..exception import FrictionlessException
from .. import settings


# TODO: support detector type when it's converted to metadata
def validate(
    source: Optional[Any] = None,
    *,
    type: Optional[str] = None,
    # Checklist
    checklist: Optional[Checklist] = None,
    checks: List[Check] = [],
    pick_errors: List[str] = [],
    skip_errors: List[str] = [],
    limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    limit_memory: int = settings.DEFAULT_LIMIT_MEMORY,
    # Validate
    resource_name: Optional[str] = None,
    original: bool = False,
    parallel: bool = False,
    **options,
):
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

    # Infer type
    if not type:
        basepath = options.get("basepath", "")
        descriptor = options.get("descriptor")
        file = system.create_file(descriptor or source, basepath=basepath)
        type = "package" if file.multipart else file.type
        if type == "table":
            type = "resource"

    # Create checklist
    if not checklist:
        checklist = Checklist(
            checks=checks,
            pick_errors=pick_errors,
            skip_errors=skip_errors,
            limit_errors=limit_errors,
            limit_memory=limit_memory,
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
            detector = Detector.from_descriptor(detector)  # type: ignore
        return detector.validate()  # type: ignore

    # Validate dialect
    elif type == "dialect":
        dialect = source
        if not isinstance(dialect, Dialect):
            dialect = Dialect.from_descriptor(dialect)  # type: ignore
        return dialect.validate()  # type: ignore

    # Validate inquiry
    elif type == "inquiry":
        inquiry = source
        if not isinstance(inquiry, Inquiry):
            # TODO: fix it
            inquiry = Inquiry.from_descriptor(inquiry)  # type: ignore
        return inquiry.validate()

    # Validate package
    elif type == "package":
        package = source
        if not isinstance(package, Package):
            package = Package(package, **options)
        if resource_name:
            resource = package.get_resource(resource_name)
            return resource.validate(checklist, original=original)
        return package.validate(checklist, original=original, parallel=parallel)

    # Validate pipeline
    elif type == "pipeline":
        pipeline = source
        if not isinstance(pipeline, Pipeline):
            pipeline = Pipeline.from_descriptor(pipeline)  # type: ignore
        return pipeline.validate()

    # Validate report
    elif type == "report":
        report = source
        if not isinstance(report, Report):
            # TODO: fix it
            report = Report.from_descriptor(report)  # type: ignore
        return report.validate()

    # Validate resource
    elif type == "resource":
        resource = source
        if not isinstance(resource, Resource):
            resource = Resource(resource, **options)
        return resource.validate(checklist, original=original)

    # Validate schema
    elif type == "schema":
        schema = source
        if not isinstance(schema, Schema):
            schema = Schema(schema, **options)
        return schema.validate()

    # Not supported
    raise FrictionlessException(f"Not supported validate type: {type}")
