from frictionless import Resource, transform, steps


# General


def test_step_cell_interpolate():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_update(name="id", type="string"),
            steps.field_update(name="population", type="string"),
            steps.cell_interpolate(template="Prefix: %s"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": "Prefix: 1", "name": "Prefix: germany", "population": "Prefix: 83"},
        {"id": "Prefix: 2", "name": "Prefix: france", "population": "Prefix: 66"},
        {"id": "Prefix: 3", "name": "Prefix: spain", "population": "Prefix: 47"},
    ]


def test_step_cell_interpolate_with_name():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.cell_interpolate(template="Prefix: %s", field_name="name"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "Prefix: germany", "population": 83},
        {"id": 2, "name": "Prefix: france", "population": 66},
        {"id": 3, "name": "Prefix: spain", "population": 47},
    ]
