import pytest

from frictionless import FrictionlessException, platform, system
from frictionless.resources import TableResource

# Bugs


def test_resource_relative_parent_path_with_trusted_option_issue_171():
    path = (
        "data/../data/table.csv"
        if not platform.type == "windows"
        else "data\\..\\data\\table.csv"
    )

    # trusted=false (default)
    with pytest.raises(FrictionlessException) as excinfo:
        TableResource.from_descriptor({"name": "name", "path": path})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('table.csv" is not safe')

    # trusted=true
    with system.use_context(trusted=True):
        resource = TableResource.from_descriptor({"name": "name", "path": path})
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
