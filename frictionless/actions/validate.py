from typing import Optional, List, Any, Union
from ..resource import Resource
from ..checklist import Checklist, Check
from .. import settings


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
    resource = Resource(source, datatype=type or "", **options)
    return resource.validate(
        checklist,
        name=name,
        limit_errors=limit_errors,
        limit_rows=limit_rows,
        parallel=parallel,
    )
