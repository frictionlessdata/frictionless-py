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


def test_step_filter_rows_petl_selectop():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id == 1")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_filter_rows_petl_selecteq():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id == 1")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_filter_rows_petl_selectne():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id != 1")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_filter_rows_petl_selectlt():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id < 2")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_filter_rows_petl_selectle():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id <= 2")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_filter_rows_petl_selectgt():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id > 2")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_filter_rows_petl_selectge():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id >= 2")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_filter_rows_petl_selectrangeopen():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.filter_rows(predicat="<formula>1 <= id <= 3")]
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_filter_rows_petl_selectrangeopenleft():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>1 <= id < 3")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_filter_rows_petl_selectrangeopenright():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>1 < id <= 3")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_filter_rows_petl_selectrangeclosed():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>1 < id < 3")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_filter_rows_petl_selectcontains():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.filter_rows(predicat="<formula>'er' in name")]
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_filter_rows_petl_selectin():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id in [1]")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_filter_rows_petl_selectnoin():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.filter_rows(predicat="<formula>id not in [2, 3]")]
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_filter_rows_petl_selectis():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id is 1")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]


def test_step_filter_rows_petl_selectisnot():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id is not 1")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_filter_rows_petl_selectisinstance():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.filter_rows(predicat=lambda row: isinstance(row["id"], int))]
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_filter_rows_petl_selectistrue():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.filter_rows(predicat=lambda row: bool(row["id"]))]
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_filter_rows_petl_selectisfalse():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.filter_rows(predicat=lambda row: not bool(row["id"]))]
    )
    assert target.schema == source.schema
    assert target.read_rows() == []


def test_step_filter_rows_petl_selectnone():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.filter_rows(predicat="<formula>id is None")])
    assert target.schema == source.schema
    assert target.read_rows() == []


def test_step_filter_rows_petl_selectisnone():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.filter_rows(predicat="<formula>id is not None")]
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_filter_rows_petl_rowlenselect():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.filter_rows(predicat=lambda row: len(row) == 3)]
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
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


def test_step_search_rows_with_anti():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.search_rows(regex=r"^f.*", anti=True)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 3, "name": "spain", "population": 47},
    ]


# Sort Rows


def test_step_sort_rows():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.sort_rows(names=["name"])])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
        {"id": 1, "name": "germany", "population": 83},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_sort_rows_with_reverse():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.sort_rows(names=["id"], reverse=True)])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 3, "name": "spain", "population": 47},
        {"id": 2, "name": "france", "population": 66},
        {"id": 1, "name": "germany", "population": 83},
    ]


# Duplicate Rows


def test_step_duplicate_rows():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.duplicate_rows()])
    assert target.schema == source.schema
    assert target.read_rows() == []


def test_step_duplicate_rows_with_name():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[steps.update_field(name="id", value=1), steps.duplicate_rows(name="id")],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 1, "name": "france", "population": 66},
        {"id": 1, "name": "spain", "population": 47},
    ]


# Unique Rows


def test_step_unique_rows():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.unique_rows()])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_unique_rows_with_name():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[steps.update_field(name="id", value=1), steps.unique_rows(name="id")],
    )
    assert target.schema == source.schema
    assert target.read_rows() == []


# Conflict Rows


def test_step_conflict_rows():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.conflict_rows(name="id")])
    assert target.schema == source.schema
    assert target.read_rows() == []


def test_step_conflict_rows_with_conflicts():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[steps.update_field(name="id", value=1), steps.conflict_rows(name="id")],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 1, "name": "france", "population": 66},
        {"id": 1, "name": "spain", "population": 47},
    ]


# Distinct Rows


def test_step_distinct_rows():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.distinct_rows(name="id")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_distinct_rows_with_distincts():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[steps.update_field(name="id", value=1), steps.distinct_rows(name="id")],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
    ]
