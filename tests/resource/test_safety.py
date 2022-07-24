import os
import pytest
from frictionless import Resource, FrictionlessException, platform


# General


@pytest.mark.xfail(reason="safety")
def test_resource_dialect_from_path_error_path_not_safe():
    dialect = os.path.abspath("data/dialect.json")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "dialect": dialect})
    error = excinfo.value.error
    assert error.type == "resource-error"
    assert error.note.count("dialect.json")


@pytest.mark.xfail(reason="safety")
def test_resource_source_path_error_bad_path_not_safe_absolute():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"path": os.path.abspath("data/table.csv")})
    error = excinfo.value.error
    assert error.type == "resource-error"
    assert error.note.count("table.csv")


@pytest.mark.xfail(reason="safety")
def test_resource_source_path_error_bad_path_not_safe_traversing():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource(
            {
                "path": "data/../data/table.csv"
                if not platform.type == "windows"
                else "data\\..\\table.csv"
            }
        )
    error = excinfo.value.error
    assert error.type == "resource-error"
    assert error.note.count("table.csv")


@pytest.mark.xfail(reason="safety")
def test_resource_relative_parent_path_with_trusted_option_issue_171():
    path = (
        "data/../data/table.csv"
        if not platform.type == "windows"
        else "data\\..\\data\\table.csv"
    )
    # trusted=false (default)
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"path": path})
    error = excinfo.value.error
    assert error.type == "resource-error"
    assert error.note.count("table.csv")
    # trusted=true
    resource = Resource({"path": path}, trusted=True)
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.xfail(reason="safety")
def test_resource_schema_from_path_error_path_not_safe():
    schema = os.path.abspath("data/schema.json")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "schema": schema})
    error = excinfo.value.error
    assert error.type == "resource-error"
    assert error.note.count("schema.json")
