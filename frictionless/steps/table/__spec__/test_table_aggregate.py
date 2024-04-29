from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_table_aggregate():
    source = TableResource(path="data/transform-groups.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_aggregate(
                group_name="name", aggregation={"sum": ("population", sum)}  # type: ignore
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "sum", "type": "any"},
        ]
    }
    assert target.read_rows() == [
        {"name": "france", "sum": 120},
        {"name": "germany", "sum": 160},
        {"name": "spain", "sum": 80},
    ]


def test_step_table_aggregate_multiple():
    source = TableResource(path="data/transform-groups.csv")
    pipeline = Pipeline(
        steps=[
            steps.table_normalize(),
            steps.table_aggregate(
                group_name="name",
                aggregation={
                    "sum": ("population", sum),  # type: ignore
                    "min": ("population", min),  # type: ignore
                    "max": ("population", max),  # type: ignore
                },
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "sum", "type": "any"},
            {"name": "min", "type": "any"},
            {"name": "max", "type": "any"},
        ]
    }
    assert target.read_rows() == [
        {"name": "france", "sum": 120, "min": 54, "max": 66},
        {"name": "germany", "sum": 160, "min": 77, "max": 83},
        {"name": "spain", "sum": 80, "min": 33, "max": 47},
    ]
