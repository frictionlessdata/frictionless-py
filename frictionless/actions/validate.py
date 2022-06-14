from typing import Optional, List, Any
from ..check import Check
from ..schema import Schema
from ..report import Report
from ..package import Package
from ..pipeline import Pipeline
from ..resource import Resource
from ..checklist import Checklist
from ..inquiry import Inquiry
from ..system import system
from ..exception import FrictionlessException
from .. import settings


# TODO: support detector type when it's converted to metadata
def validate(
    source: Any,
    *,
    type: Optional[str] = None,
    # Checklist
    checklist: Optional[Checklist] = None,
    checks: Optional[List[Check]] = None,
    pick_errors: Optional[List[str]] = None,
    skip_errors: Optional[List[str]] = None,
    limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    limit_memory: int = settings.DEFAULT_LIMIT_MEMORY,
    keep_original: bool = False,
    # Validate
    resource_name: Optional[str] = None,
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
            keep_original=keep_original,
        )

    # Validate checklist
    if type == "checklist":
        checklist = source
        if not isinstance(checklist, Checklist):
            checklist = Checklist(checklist, **options)
        return checklist.validate()

    # Validate inquiry
    elif type == "inquiry":
        inquiry = source
        if not isinstance(inquiry, Inquiry):
            inquiry = Inquiry.from_descriptor(inquiry)
        return inquiry.validate()

    # Validate package
    elif type == "package":
        package = source
        if not isinstance(package, Package):
            package = Package(package, **options)
        if resource_name:
            resource = package.get_resource(resource_name)
            return resource.validate(checklist)
        return package.validate(checklist, parallel=parallel)

    # Validate pipeline
    elif type == "pipeline":
        pipeline = source
        if not isinstance(pipeline, Pipeline):
            pipeline = Pipeline(pipeline, **options)
        return pipeline.validate()

    # Validate report
    elif type == "report":
        report = source
        if not isinstance(report, Inquiry):
            report = Report.from_descriptor(report)
        return report.validate()

    # Validate resource
    elif type == "resource":
        resource = source
        if not isinstance(resource, Resource):
            resource = Resource(resource, **options)
        return resource.validate(checklist)

    # Validate schema
    elif type == "schema":
        schema = source
        if not isinstance(schema, Schema):
            schema = Schema(schema, **options)
        return schema.validate()

    # Not supported
    raise FrictionlessException(f"Not supported validate type: {type}")
