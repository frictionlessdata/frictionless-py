from typing import Optional, List, Any
from ..check import Check
from ..schema import Schema
from ..package import Package
from ..pipeline import Pipeline
from ..checklist import Checklist
from ..inquiry import Inquiry
from ..system import system
from ..resource import Resource
from ..exception import FrictionlessException
from .. import settings


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

    # TODO: support detector type when it's converted to metadata
    # Validate object
    if type == "checklist":
        if not isinstance(source, Checklist):
            source = Checklist(source, **options)
        return source.validate()
    elif type == "inquiry":
        if not isinstance(source, Inquiry):
            source = Inquiry(source, **options)  # type: ignore
        return source.validate()  # type: ignore
    elif type == "package":
        if not isinstance(source, Package):
            source = Package(source, **options)
        if resource_name:
            resource = source.get_resource(resource_name)
            return resource.validate(checklist)
        return source.validate(checklist, parallel=parallel)
    elif type == "pipeline":
        if not isinstance(source, Pipeline):
            source = Pipeline(source, **options)
        return source.validate()
    elif type == "resource":
        if not isinstance(source, Resource):
            source = Resource(source, **options)
        return source.validate(checklist)
    elif type == "schema":
        if not isinstance(source, Schema):
            source = Schema(source, **options)
        return source.validate()

    # Not supported
    raise FrictionlessException(f"Not supported validate type: {type}")
