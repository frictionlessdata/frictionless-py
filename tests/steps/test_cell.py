from frictionless import Resource, transform, steps


# Pick Fields


def test_step_replace_cells():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.replace_cells(source="france", target="FRANCE")]
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "FRANCE", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_replace_cells_with_name():
    source = Resource(path="data/transform.csv")
    target = transform(
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


# Fill Cells


def test_step_fill_cells():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.replace_cells(source="france", target=None),
            steps.fill_cells(name="name", value="FRANCE"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "FRANCE", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_fill_cells_direction_down():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.replace_cells(source="france", target=None),
            steps.fill_cells(direction="down"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "germany", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_fill_cells_direction_right():
    source = Resource(path="data/transform.csv")
    source.infer(only_sample=True)
    source.schema.get_field("id").type = "string"
    source.schema.get_field("population").type = "string"
    target = transform(
        source,
        steps=[
            steps.replace_cells(source="france", target=None),
            steps.fill_cells(direction="right"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": "1", "name": "germany", "population": "83"},
        {"id": "2", "name": "2", "population": "66"},
        {"id": "3", "name": "spain", "population": "47"},
    ]


def test_step_fill_cells_direction_left():
    source = Resource(path="data/transform.csv")
    source.infer(only_sample=True)
    source.schema.get_field("id").type = "string"
    source.schema.get_field("population").type = "string"
    target = transform(
        source,
        steps=[
            steps.replace_cells(source="france", target=None),
            steps.fill_cells(direction="left"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": "1", "name": "germany", "population": "83"},
        {"id": "2", "name": "66", "population": "66"},
        {"id": "3", "name": "spain", "population": "47"},
    ]
