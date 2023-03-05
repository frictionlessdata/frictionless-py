from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from ..exception import FrictionlessException
from ..checklist import Checklist
from ..report import Report
from .. import helpers

if TYPE_CHECKING:
    from .resource import Resource
    from ..error import Error


# Remove duplication from table validate function
def validate(resource: Resource, checklist: Optional[Checklist] = None):
    # Create state
    partial = False
    timer = helpers.Timer()
    labels: List[str] = []
    errors: List[Error] = []
    warnings: List[str] = []

    # Prepare checklist
    checklist = checklist or Checklist()
    checks = checklist.connect(resource)

    # Validate metadata
    try:
        resource.to_descriptor()
    except FrictionlessException as exception:
        return Report.from_validation_task(
            resource, time=timer.time, errors=exception.to_errors()
        )

    # TODO: remove in next version
    # Ignore not-supported hashings
    if resource.hash is not None:
        algorithm, _ = helpers.parse_resource_hash_v1(resource.hash)
        if algorithm not in ["md5", "sha256"]:
            warning = "hash is ignored; supported algorithms: md5/sha256"
            warnings.append(warning)

    # Prepare resource
    if resource.closed:
        try:
            resource.open()
        except FrictionlessException as exception:
            resource.close()
            return Report.from_validation_task(
                resource, time=timer.time, errors=exception.to_errors()
            )

    # Validate data
    with resource:
        # Validate start
        for index, check in enumerate(checks):
            for error in check.validate_start():
                if error.type == "check-error":
                    del checks[index]
                if checklist.match(error):
                    errors.append(error)

        # Validate file
        if resource.hash is not None or resource.bytes is not None:
            helpers.pass_through(resource.byte_stream)

        # Validate end
        if not partial:
            for check in checks:
                for error in check.validate_end():
                    if checklist.match(error):
                        errors.append(error)

    # Return report
    return Report.from_validation_task(
        resource, time=timer.time, labels=labels, errors=errors, warnings=warnings
    )
