from frictionless import Pipeline, Step, steps
from frictionless.resources import TableResource

# General


def test_step_row_subset_conflicts():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_subset(subset="conflicts", field_name="id"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == []


def test_step_row_subset_conflicts_with_duplicates():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", value=1),
            steps.row_subset(subset="conflicts", field_name="id"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 1, "name": "france", "population": 66},
        {"id": 1, "name": "spain", "population": 47},
    ]


def test_step_row_subset_distinct():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_subset(subset="distinct", field_name="id"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_row_subset_distinct_with_duplicates():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", value=1),
            steps.row_subset(subset="distinct", field_name="id"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_row_subset_duplicates():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_subset(subset="duplicates"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == []


def test_step_row_subset_duplicates_with_name():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", value=1),
            steps.row_subset(subset="duplicates", field_name="id"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 1, "name": "france", "population": 66},
        {"id": 1, "name": "spain", "population": 47},
    ]


def test_step_row_subset_unique():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.row_subset(subset="unique"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_row_subset_unique_with_name():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.field_update(name="id", value=1),
            steps.row_subset(subset="unique", field_name="id"),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == []


# Bugs


def test_step_row_subset_conflicts_from_descriptor_issue_996():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            Step.from_descriptor(
                {"type": "row-subset", "subset": "conflicts", "fieldName": "id"}
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == []
