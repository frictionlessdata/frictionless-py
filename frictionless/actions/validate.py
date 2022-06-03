import types
import inspect
import warnings
from typing import Optional, List, Any
from ..check import Check
from ..schema import Schema
from ..package import Package
from ..pipeline import Pipeline
from ..inquiry import Inquiry, InquiryTask
from ..system import system
from ..resource import Resource
from ..report import Report, ReportTask
from ..errors import TaskError
from ..exception import FrictionlessException
from .. import helpers
from .. import settings
from .. import errors


# TODO: here we'd like to accept both inquiry + individual options


@Report.from_validate
def validate(
    source: Optional[Any] = None,
    type: Optional[str] = None,
    checks: Optional[List[Check]] = None,
    # TODO: don't provide as options only as a part of inquiry?
    pick_errors: Optional[List[str]] = None,
    skip_errors: Optional[List[str]] = None,
    limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    limit_memory: int = settings.DEFAULT_LIMIT_MEMORY,
    original: bool = False,
    # Package
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

    # TODO: support detector type when it's converted to metadata
    # Validate object
    if type == "inquiry":
        inquiry = Inquiry(source)
        return inquiry.validate()
    elif type == "package":
        package = Package(source, **options)
        return package.validate(
            original=original,
            parallel=parallel,
            resource_name=resource_name,
        )
    elif type == "pipeline":
        pipeline = Pipeline(source)
        return pipeline.validate()
    elif type == "resource":
        resource = Resource(source, **options)
        return resource.validate(
            original=original,
            checks=checks,
            pick_errors=pick_errors,
            skip_errors=skip_errors,
            limit_errors=limit_errors,
            limit_memory=limit_memory,
        )
    elif type == "schema":
        schema = Schema(source)
        return schema.validate()

    # Not supported
    note = f"Not supported validate type: {type}"
    raise FrictionlessException(errors.GeneralError(note=note))
