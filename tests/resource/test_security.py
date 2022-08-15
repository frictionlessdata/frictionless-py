import os
import pytest
from frictionless import Resource, FrictionlessException, platform, system


# General


def test_resource_source_path_error_bad_path_not_safe_absolute():
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"path": os.path.abspath("data/table.csv")})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('table.csv" is not safe')


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
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('table.csv" is not safe')


def test_resource_dialect_from_path_error_path_not_safe():
    dialect = os.path.abspath("data/dialect.json")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "dialect": dialect})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('dialect.json" is not safe')


def test_resource_schema_from_path_error_path_not_safe():
    schema = os.path.abspath("data/schema.json")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "schema": schema})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('schema.json" is not safe')


def test_resource_checklist_from_path_error_path_not_safe():
    checklist = os.path.abspath("data/checklist.json")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "checklist": checklist})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('checklist.json" is not safe')


def test_resource_pipeline_from_path_error_path_not_safe():
    pipeline = os.path.abspath("data/pipeline.json")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "pipeline": pipeline})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('pipeline.json" is not safe')


def test_resource_extrapaths_error_bad_path_not_safe_absolute():
    extrapath = os.path.abspath("data/chunk2.csv")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "extrapaths": [extrapath]})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('chunk2.csv" is not safe')


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_extrapaths_error_bad_path_not_safe_traversing():
    extrapath = "data/../chunk2.csv"
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "extrapaths": [extrapath]})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('chunk2.csv" is not safe')


def test_resource_profiles_error_bad_path_not_safe_absolute():
    profile = os.path.abspath("data/profiles/camtrap.json")
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "profiles": [profile]})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('camtrap.json" is not safe')


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_profiles_error_bad_path_not_safe_traversing():
    profile = "data/profiles/../profiles/camtrap.json"
    with pytest.raises(FrictionlessException) as excinfo:
        Resource({"name": "name", "path": "path", "profiles": [profile]})
    error = excinfo.value.error
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('camtrap.json" is not safe')


# Bugs


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
    reasons = excinfo.value.reasons
    assert len(reasons) == 1
    assert error.type == "resource-error"
    assert error.note == "descriptor is not valid"
    assert reasons[0].type == "resource-error"
    assert reasons[0].note.count('table.csv" is not safe')

    # trusted=true
    with system.use_context(trusted=True):
        resource = Resource({"path": path})
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
