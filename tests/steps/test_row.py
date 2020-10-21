from frictionless import Resource, transform, steps


# Head


def test_step_head_rows():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.head_rows(limit=2)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
    ]


# Tail


def test_step_tail_rows():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.tail_rows(limit=2)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


# Slice


def test_step_slice_rows():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.slice_rows(stop=2)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_slice_with_start():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.slice_rows(start=1, stop=2)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_slice_with_start_and_step():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.slice_rows(start=1, stop=3, step=2)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
    ]


# Filter Rows


def test_step_filter_rows():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id > 1")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_filter_rows_with_callable_predicat():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.filter_rows(predicat=lambda row: row["id"] > 1)]
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


# Search Rows


def test_step_search_rows():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.search_rows(regex=r"^f.*")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_search_rows_with_name():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.search_rows(regex=r"^f.*", name="name")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
    ]
