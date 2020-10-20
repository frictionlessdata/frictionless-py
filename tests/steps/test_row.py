from frictionless import Resource, transform_resource, steps


# Head


def test_step_head_rows():
    source = Resource(path="data/transform.csv")
    target = transform_resource(source, steps=[steps.head_rows(limit=2)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
    ]


# Tail


def test_step_tail_rows():
    source = Resource(path="data/transform.csv")
    target = transform_resource(source, steps=[steps.tail_rows(limit=2)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


# Slice


def test_step_slice_rows():
    source = Resource(path="data/transform.csv")
    target = transform_resource(source, steps=[steps.slice_rows(stop=2)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_slice_with_start():
    source = Resource(path="data/transform.csv")
    target = transform_resource(source, steps=[steps.slice_rows(start=1, stop=2)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_slice_with_start_and_step():
    source = Resource(path="data/transform.csv")
    target = transform_resource(source, steps=[steps.slice_rows(start=1, stop=3, step=2)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
    ]
