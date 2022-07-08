import pytest


from frictionless import Resource, transform, steps


# General


@pytest.mark.parametrize(
    "scenario",
    [
        {
            "test_id": "idem",
            "csv_path": "data/transform.csv",
            "names": ["id", "name", "population"],
            "expected_schema": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"},
                    {"name": "population", "type": "integer"},
                ]
            },
            "expected_rows": [
                {"id": 1, "name": "germany", "population": 83},
                {"id": 2, "name": "france", "population": 66},
                {"id": 3, "name": "spain", "population": 47},
            ],
        },
        {
            "test_id": "reverse_field_order",
            "csv_path": "data/transform.csv",
            "names": ["population", "name", "id"],
            "expected_schema": {
                "fields": [
                    {"name": "population", "type": "integer"},
                    {"name": "name", "type": "string"},
                    {"name": "id", "type": "integer"},
                ]
            },
            "expected_rows": [
                {"population": 83, "name": "germany", "id": 1},
                {"population": 66, "name": "france", "id": 2},
                {"population": 47, "name": "spain", "id": 3},
            ],
        },
        {
            "test_id": "remove_last_column",
            "csv_path": "data/transform.csv",
            "names": ["id", "name"],
            "expected_schema": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"},
                ]
            },
            "expected_rows": [
                {"id": 1, "name": "germany"},
                {"id": 2, "name": "france"},
                {"id": 3, "name": "spain"},
            ],
        },
        {
            "test_id": "changed_field_order",
            "csv_path": "data/transform.csv",
            "names": ["name", "id"],
            "expected_schema": {
                "fields": [
                    {"name": "name", "type": "string"},
                    {"name": "id", "type": "integer"},
                ]
            },
            "expected_rows": [
                {"name": "germany", "id": 1},
                {"name": "france", "id": 2},
                {"name": "spain", "id": 3},
            ],
        },
        {
            "test_id": "missing_name",
            "csv_path": "data/transform.csv",
            "names": ["name", "nonexistent"],
            "expected_schema": {
                "fields": [
                    {"name": "name", "type": "string"},
                ]
            },
            "expected_rows": [
                {"name": "germany"},
                {"name": "france"},
                {"name": "spain"},
            ],
        },
        {
            "test_id": "no_fields",
            "csv_path": "data/transform.csv",
            "names": [],
            "expected_schema": {"fields": []},
            "expected_rows": [
                {},
                {},
                {},
            ],
        },
    ],
    ids=lambda scenario: scenario["test_id"],
)
def test_step_field_filter(scenario):
    csv_path = scenario["csv_path"]
    names = scenario["names"]
    expected_schema = scenario["expected_schema"]
    expected_rows = scenario["expected_rows"]

    source = Resource(path=csv_path)
    target = transform(
        source,
        steps=[
            steps.field_filter(names=names),
        ],
    )
    assert target.schema == expected_schema
    assert target.read_rows() == expected_rows
