from frictionless import Resource, steps


# General


def test_step_cell_convert():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_update(name="id", type="string"),
            steps.field_update(name="population", type="string"),
            steps.cell_convert(value="n/a"),
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
        {"id": "n/a", "name": "n/a", "population": "n/a"},
        {"id": "n/a", "name": "n/a", "population": "n/a"},
        {"id": "n/a", "name": "n/a", "population": "n/a"},
    ]


def test_step_cell_convert_with_field_name():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.cell_convert(value="n/a", field_name="name"),
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
        {"id": 1, "name": "n/a", "population": 83},
        {"id": 2, "name": "n/a", "population": 66},
        {"id": 3, "name": "n/a", "population": 47},
    ]
