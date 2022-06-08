from typing import Optional, List, Any
from ..check import Check
from ..schema import Schema
from ..package import Package
from ..pipeline import Pipeline
from ..checklist import Checklist
from ..inquiry import Inquiry
from ..system import system
from ..resource import Resource
from ..report import Report
from ..exception import FrictionlessException
from .. import settings
from .. import errors


def validate(
    source: Optional[Any] = None,
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
    allow_parallel: bool = False,
    # Package
    resource_name: Optional[str] = None,
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
            allow_parallel=allow_parallel,
        )

    # TODO: support detector type when it's converted to metadata
    # Validate object
    if type == "inquiry":
        inquiry = Inquiry(source)
        return inquiry.validate()
    elif type == "package":
        package = Package(source, **options)
        if resource_name:
            resource = package.get_resource(resource_name)
            return resource.validate(checklist)
        return package.validate(checklist)
    elif type == "pipeline":
        pipeline = Pipeline(source)
        return pipeline.validate()
    elif type == "resource":
        resource = Resource(source, **options)
        return resource.validate(checklist)
    elif type == "schema":
        schema = Schema(source)
        return schema.validate()

    # Not supported
    note = f"Not supported validate type: {type}"
    raise FrictionlessException(errors.GeneralError(note=note))
