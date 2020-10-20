from frictionless import Resource, transform_resource, steps


# Pick Fields


def test_step_replace_cells():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source, steps=[steps.replace_cells(source="france", target="FRANCE")]
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "FRANCE", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_replace_cells_with_name():
    source = Resource(path="data/transform.csv")
    target = transform_resource(
        source, steps=[steps.replace_cells(source="france", target="FRANCE", name="id")]
    )
    assert target.schema == {
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
