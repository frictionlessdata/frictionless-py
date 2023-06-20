from typing import Any, List, Optional, Union

from .. import settings
from ..checklist import Check, Checklist
from ..exception import FrictionlessException
from ..report import Report
from ..resource import Resource


def validate(
    source: Optional[Any] = None,
    *,
    name: Optional[str] = None,
    type: Optional[str] = None,
    # Checklist
    checklist: Optional[Union[Checklist, str]] = None,
    checks: List[Check] = [],
    pick_errors: List[str] = [],
    skip_errors: List[str] = [],
    # Validate
    limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    limit_rows: Optional[int] = None,
    parallel: bool = False,
    # Deprecated
    resource_name: Optional[str] = None,
    **options: Any,
):
    """Validate resource

    Parameters:
        source (dict|str): a data source
        type (str): source type - inquiry, package, resource, schema or table
        **options (dict): options for the underlaying function

    Returns:
        Report: validation report
    """
    name = name or resource_name

    # Create checklist
    if isinstance(checklist, str):
        checklist = Checklist.from_descriptor(checklist)
    elif not checklist:
        checklist = Checklist(
            checks=checks,
            pick_errors=pick_errors,
            skip_errors=skip_errors,
        )

    # Create resource
    try:
        # Create resource
        resource = (
            source
            if isinstance(source, Resource)
            else Resource(source, datatype=type, **options)
        )
    except FrictionlessException as exception:
        errors = exception.reasons if exception.reasons else [exception.error]
        return Report.from_validation(errors=errors)

    # Validate resource
    return resource.validate(
        checklist,
        name=name,
        parallel=parallel,
        limit_rows=limit_rows,
        limit_errors=limit_errors,
    )
