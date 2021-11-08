import pytest
from frictionless import Resource, FrictionlessException, transform, steps


# Aggregate


def test_step_table_aggregate():
    source = Resource("data/transform-groups.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_aggregate(
                group_name="name", aggregation={"sum": ("population", sum)}
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "sum"},
        ]
    }
    assert target.read_rows() == [
        {"name": "france", "sum": 120},
        {"name": "germany", "sum": 160},
        {"name": "spain", "sum": 80},
    ]


def test_step_table_aggregate_multiple():
    source = Resource("data/transform-groups.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_aggregate(
                group_name="name",
                aggregation={
                    "sum": ("population", sum),
                    "min": ("population", min),
                    "max": ("population", max),
                },
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "sum"},
            {"name": "min"},
            {"name": "max"},
        ]
    }
    assert target.read_rows() == [
        {"name": "france", "sum": 120, "min": 54, "max": 66},
        {"name": "germany", "sum": 160, "min": 77, "max": 83},
        {"name": "spain", "sum": 80, "min": 33, "max": 47},
    ]


# Attach


def test_step_table_attach():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_attach(resource=Resource(data=[["note"], ["large"], ["mid"]]))
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "large"},
        {"id": 2, "name": "france", "population": 66, "note": "mid"},
        {"id": 3, "name": "spain", "population": 47, "note": None},
    ]


def test_step_table_attach_from_dict():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[steps.table_attach(resource=dict(data=[["note"], ["large"], ["mid"]]))],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "large"},
        {"id": 2, "name": "france", "population": 66, "note": "mid"},
        {"id": 3, "name": "spain", "population": 47, "note": None},
    ]


# Diff


def test_step_table_diff():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_diff(
                resource=Resource(
                    data=[
                        ["id", "name", "population"],
                        [1, "germany", 83],
                        [2, "france", 50],
                        [3, "spain", 47],
                    ]
                )
            ),
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
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_table_diff_from_dict():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_diff(
                resource=dict(
                    data=[
                        ["id", "name", "population"],
                        [1, "germany", 83],
                        [2, "france", 50],
                        [3, "spain", 47],
                    ]
                )
            ),
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
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_table_diff_with_ignore_order():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_diff(
                resource=Resource(
                    data=[
                        ["name", "id", "population"],
                        ["germany", "1", "83"],
                        ["france", "2", "50"],
                        ["spain", "3", "47"],
                    ]
                ),
                ignore_order=True,
            ),
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
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_table_diff_with_use_hash():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_diff(
                resource=Resource(
                    data=[
                        ["id", "name", "population"],
                        [1, "germany", 83],
                        [2, "france", 50],
                        [3, "spain", 47],
                    ]
                ),
                use_hash=True,
            ),
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
        {"id": 2, "name": "france", "population": 66},
    ]


# Intersect


def test_step_table_intersect():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_intersect(
                resource=Resource(
                    data=[
                        ["id", "name", "population"],
                        [1, "germany", 83],
                        [2, "france", 50],
                        [3, "spain", 47],
                    ]
                )
            ),
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
        {"id": 1, "name": "germany", "population": 83},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_table_intersect_from_dict():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_intersect(
                resource=dict(
                    data=[
                        ["id", "name", "population"],
                        [1, "germany", 83],
                        [2, "france", 50],
                        [3, "spain", 47],
                    ]
                )
            ),
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
        {"id": 1, "name": "germany", "population": 83},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_table_intersect_with_use_hash():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_intersect(
                resource=Resource(
                    data=[
                        ["id", "name", "population"],
                        [1, "germany", 83],
                        [2, "france", 50],
                        [3, "spain", 47],
                    ]
                ),
                use_hash=True,
            ),
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
        {"id": 1, "name": "germany", "population": 83},
        {"id": 3, "name": "spain", "population": 47},
    ]


# Join


def test_step_table_join():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                field_name="id",
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
    ]


def test_step_table_join_from_dict():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=dict(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                field_name="id",
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
    ]


def test_step_table_join_with_name_is_not_first_field():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_join(
                resource=Resource(
                    data=[["name", "note"], ["germany", "beer"], ["france", "vine"]]
                ),
                field_name="name",
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
    ]


def test_step_table_join_mode_left():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                field_name="id",
                mode="left",
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
        {"id": 3, "name": "spain", "population": 47, "note": None},
    ]


def test_step_table_join_mode_right():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=Resource(data=[["id", "note"], [1, "beer"], [4, "rum"]]),
                field_name="id",
                mode="right",
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 4, "name": None, "population": None, "note": "rum"},
    ]


def test_step_table_join_mode_outer():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=Resource(data=[["id", "note"], [1, "beer"], [4, "rum"]]),
                field_name="id",
                mode="outer",
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": None},
        {"id": 3, "name": "spain", "population": 47, "note": None},
        {"id": 4, "name": None, "population": None, "note": "rum"},
    ]


def test_step_table_join_mode_cross():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_join(
                resource=Resource(data=[["id2", "note"], [1, "beer"], [4, "rum"]]),
                mode="cross",
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "id2", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "id2": 1, "note": "beer"},
        {"id": 1, "name": "germany", "population": 83, "id2": 4, "note": "rum"},
        {"id": 2, "name": "france", "population": 66, "id2": 1, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "id2": 4, "note": "rum"},
        {"id": 3, "name": "spain", "population": 47, "id2": 1, "note": "beer"},
        {"id": 3, "name": "spain", "population": 47, "id2": 4, "note": "rum"},
    ]


def test_step_table_join_mode_negate():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_join(
                resource=Resource(data=[["id", "note"], ["1", "beer"], ["4", "rum"]]),
                mode="negate",
            ),
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
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_table_join_hash_is_true():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_join(
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                field_name="id",
                use_hash=True,
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": "beer"},
        {"id": 2, "name": "france", "population": 66, "note": "vine"},
    ]


# Melt


def test_step_table_melt():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="name"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "variable"},
            {"name": "value"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "variable": "id", "value": 1},
        {"name": "germany", "variable": "population", "value": 83},
        {"name": "france", "variable": "id", "value": 2},
        {"name": "france", "variable": "population", "value": 66},
        {"name": "spain", "variable": "id", "value": 3},
        {"name": "spain", "variable": "population", "value": 47},
    ]


def test_step_table_melt_with_variables():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="name", variables=["population"]),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "variable"},
            {"name": "value"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "variable": "population", "value": 83},
        {"name": "france", "variable": "population", "value": 66},
        {"name": "spain", "variable": "population", "value": 47},
    ]


def test_step_table_melt_with_to_field_names():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_melt(
                field_name="name", variables=["population"], to_field_names=["key", "val"]
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "key"},
            {"name": "val"},
        ]
    }
    assert target.read_rows() == [
        {"name": "germany", "key": "population", "val": 83},
        {"name": "france", "key": "population", "val": 66},
        {"name": "spain", "key": "population", "val": 47},
    ]


# Merge


def test_step_table_merge():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_merge(
                resource=Resource(data=[["id", "name", "note"], [4, "malta", "island"]])
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": None},
        {"id": 2, "name": "france", "population": 66, "note": None},
        {"id": 3, "name": "spain", "population": 47, "note": None},
        {"id": 4, "name": "malta", "population": None, "note": "island"},
    ]


def test_step_table_merge_from_dict():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_merge(
                resource=dict(data=[["id", "name", "note"], [4, "malta", "island"]])
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "note", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83, "note": None},
        {"id": 2, "name": "france", "population": 66, "note": None},
        {"id": 3, "name": "spain", "population": 47, "note": None},
        {"id": 4, "name": "malta", "population": None, "note": "island"},
    ]


def test_step_table_merge_with_field_names():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_merge(
                resource=Resource(data=[["id", "name", "note"], [4, "malta", "island"]]),
                field_names=["id", "name"],
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany"},
        {"id": 2, "name": "france"},
        {"id": 3, "name": "spain"},
        {"id": 4, "name": "malta"},
    ]


def test_step_merge_ignore_fields():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_merge(
                resource=Resource(data=[["id2", "name2"], [4, "malta"]]),
                ignore_fields=True,
            ),
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
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
        {"id": 4, "name": "malta", "population": None},
    ]


def test_step_table_merge_with_sort():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_merge(
                resource=Resource(data=[["id", "name", "population"], [4, "malta", 1]]),
                sort_by_field=["population"],
            ),
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
        {"id": 4, "name": "malta", "population": 1},
        {"id": 3, "name": "spain", "population": 47},
        {"id": 2, "name": "france", "population": 66},
        {"id": 1, "name": "germany", "population": 83},
    ]


# Pivot


def test_step_table_pivot():
    source = Resource("data/transform-pivot.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_pivot(f1="region", f2="gender", f3="units", aggfun=sum),
        ],
    )
    print(target.schema)
    assert target.schema == {
        "fields": [
            {"name": "region", "type": "string"},
            {"name": "boy", "type": "integer"},
            {"name": "girl", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"region": "east", "boy": 33, "girl": 29},
        {"region": "west", "boy": 35, "girl": 23},
    ]


# Recast


def test_step_table_recast():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="id"),
            steps.table_recast(field_name="id"),
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
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


# Transpose


def test_step_table_transpose():
    source = Resource("data/transpose.csv")
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_transpose(),
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
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


# Validate


def test_step_table_validate():
    source = Resource("data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.cell_set(field_name="population", value="bad"),
            steps.table_validate(),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    with pytest.raises(FrictionlessException) as excinfo:
        target.read_rows()
    error = excinfo.value.error
    assert error.code == "step-error"
    assert error.note.count('type is "integer/default"')


# Write


def test_step_table_write(tmpdir):
    path = str(tmpdir.join("table.json"))

    # Write
    source = Resource("data/transform.csv")
    transform(
        source,
        steps=[
            steps.cell_set(field_name="population", value=100),
            steps.table_write(path=path),
        ],
    )

    # Read
    resource = Resource(path=path)
    assert resource.read_rows() == [
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]
