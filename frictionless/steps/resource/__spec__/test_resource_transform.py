import json

import pytest

from frictionless import FrictionlessException, Package, Pipeline, steps

# General


def test_step_resource_transform_from_descriptor():
    descriptor = {
        "steps": [
            {
                "type": "resource-transform",
                "name": "data",
                "steps": [
                    {"type": "cell-set", "fieldName": "description", "value": "Updated"},
                    {"type": "cell-set", "fieldName": "amount", "value": 0},
                ],
            }
        ]
    }
    pipeline = Pipeline.from_descriptor(descriptor)
    nested = pipeline.steps[0]
    assert isinstance(nested, steps.resource_transform)
    assert all(isinstance(step, steps.cell_set) for step in nested.steps)
    assert pipeline.to_descriptor() == descriptor
    target = Package("data/package/datapackage.json").transform(pipeline)
    assert target.get_table_resource("data").read_rows() == [
        {"id": "A3001", "name": "Taxes", "description": "Updated", "amount": 0},
        {"id": "A5032", "name": "Parking Fees", "description": "Updated", "amount": 0},
    ]


def test_step_resource_transform_json_round_trip(tmp_path):
    pipeline = Pipeline(
        steps=[
            steps.resource_transform(
                name="data",
                steps=[steps.cell_set(field_name="amount", value=0)],
            )
        ]
    )
    descriptor = json.loads(pipeline.to_json())
    assert descriptor["steps"][0]["steps"] == [
        {"type": "cell-set", "fieldName": "amount", "value": 0}
    ]
    path = tmp_path / "pipeline.json"
    path.write_text(json.dumps(descriptor), encoding="utf-8")
    restored = Pipeline.from_descriptor(str(path))
    source = Package("data/package/datapackage.json")
    restored_rows = source.transform(restored).get_table_resource("data").read_rows()
    original_rows = source.transform(pipeline).get_table_resource("data").read_rows()
    assert [row.to_dict() for row in restored_rows] == [
        row.to_dict() for row in original_rows
    ]


def test_step_resource_transform_descriptor_empty_steps():
    descriptor = {"steps": [{"type": "resource-transform", "name": "data", "steps": []}]}
    pipeline = Pipeline.from_descriptor(descriptor)
    assert pipeline.to_descriptor() == descriptor
    source = Package("data/package/datapackage.json")
    transformed_rows = source.transform(pipeline).get_table_resource("data").read_rows()
    original_rows = source.get_table_resource("data").read_rows()
    assert [row.to_dict() for row in transformed_rows] == [
        row.to_dict() for row in original_rows
    ]


def test_step_resource_transform_invalid_nested_descriptor():
    descriptor = {
        "steps": [
            {
                "type": "resource-transform",
                "name": "data",
                "steps": [{"type": "cell-set", "fieldName": 42, "value": 0}],
            }
        ]
    }
    with pytest.raises(FrictionlessException, match="fieldName"):
        Pipeline.from_descriptor(descriptor)


def test_step_resource_transform():
    source = Package("data/package/datapackage.json")
    pipeline = Pipeline(
        steps=[
            steps.resource_update(name="data", descriptor={"title": "It's our data"}),
            steps.resource_remove(name="data2"),
            steps.resource_add(name="data2", descriptor={"path": "data2.csv"}),
            steps.resource_transform(
                name="data",
                steps=[
                    steps.cell_set(field_name="description", value="Zeroed"),
                    steps.cell_set(field_name="amount", value=0),
                ],
            ),
            steps.resource_transform(
                name="data2",
                steps=[
                    steps.cell_set(field_name="comment", value="It works!"),
                ],
            ),
        ],
    )
    target = source.transform(pipeline)
    assert target.resource_names == ["data", "data2"]
    assert target.get_table_resource("data").read_rows() == [
        {"id": "A3001", "name": "Taxes", "description": "Zeroed", "amount": 0},
        {"id": "A5032", "name": "Parking Fees", "description": "Zeroed", "amount": 0},
    ]
    assert target.get_table_resource("data2").read_rows() == [
        {"parent": "A3001", "comment": "It works!"},
        {"parent": "A3001", "comment": "It works!"},
        {"parent": "A5032", "comment": "It works!"},
    ]
