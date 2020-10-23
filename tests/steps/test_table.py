from frictionless import Resource, transform, steps


# Merge Tables


def test_step_merge_tables():
    # TODO: renamed population header to people
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.merge_tables(
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


def test_step_merge_tables_with_names():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.merge_tables(
                resource=Resource(data=[["id", "name", "note"], [4, "malta", "island"]]),
                names=["id", "name"],
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


def test_step_merge_ignore_names():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.merge_tables(
                resource=Resource(data=[["id2", "name2"], [4, "malta"]]),
                ignore_names=True,
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


def test_step_merge_tables_with_sort():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.merge_tables(
                resource=Resource(data=[["id", "name", "population"], [4, "malta", 1]]),
                sort=["population"],
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


# Join Tables


def test_step_join_tables():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.join_tables(
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                name="id",
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


def test_step_join_tables_with_name_is_not_first_field():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.join_tables(
                resource=Resource(
                    data=[["name", "note"], ["germany", "beer"], ["france", "vine"]]
                ),
                name="name",
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


def test_step_join_tables_mode_left():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.join_tables(
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                name="id",
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


def test_step_join_tables_mode_right():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.join_tables(
                resource=Resource(data=[["id", "note"], [1, "beer"], [4, "rum"]]),
                name="id",
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


def test_step_join_tables_mode_outer():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.join_tables(
                resource=Resource(data=[["id", "note"], [1, "beer"], [4, "rum"]]),
                name="id",
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


def test_step_join_tables_mode_cross():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.join_tables(
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


def test_step_join_tables_mode_anti():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.join_tables(
                resource=Resource(data=[["id", "note"], [1, "beer"], [4, "rum"]]),
                mode="anti",
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


def test_step_join_tables_hash_is_true():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.join_tables(
                resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
                name="id",
                hash=True,
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


# Attach Tables


def test_step_attach_tables():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.attach_tables(resource=Resource(data=[["note"], ["large"], ["mid"]]))
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


# Diff Tables


def test_step_diff_tables():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.diff_tables(
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
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_diff_tables_with_ignore_order():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.diff_tables(
                resource=Resource(
                    data=[
                        ["name", "id", "population"],
                        ["germany", 1, 83],
                        ["france", 2, 50],
                        ["spain", 3, 47],
                    ]
                ),
                ignore_order=True,
            ),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
    ]


def test_step_diff_tables_with_use_hash():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.diff_tables(
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
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 2, "name": "france", "population": 66},
    ]


# Intersect Tables


def test_step_intersect_tables():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.intersect_tables(
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
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_intersect_tables_with_use_hash():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.intersect_tables(
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
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 3, "name": "spain", "population": 47},
    ]


# Aggregate Table


def test_step_aggregate_table():
    source = Resource(path="data/transform-groups.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.aggregate_table(
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


def test_step_aggregate_table_multiple():
    source = Resource(path="data/transform-groups.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.aggregate_table(
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


# Melt Table


def test_step_melt_table():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.melt_table(name="name"),
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


def test_step_melt_table_with_variables():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.melt_table(name="name", variables=["population"]),
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


def test_step_melt_table_with_to_names():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.melt_table(
                name="name", variables=["population"], to_names=["key", "val"]
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


# Recast Table


def test_step_recast_table():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.melt_table(name="id"),
            steps.recast_table(name="id"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


# Transpose Table


# TODO: fix this step
def test_step_transpose_table():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.transpose_table(),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "name", "type": "string"},
            {"name": "germany", "type": "integer"},
            {"name": "france", "type": "integer"},
            {"name": "spain", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"name": "population", "germany": 83, "france": 66, "spain": 47}
    ]


# Pivot Table


def test_step_pivot_table():
    source = Resource(path="data/transform-pivot.csv")
    target = transform(
        source,
        steps=[
            steps.normalize_table(),
            steps.pivot_table(f1="region", f2="gender", f3="units", aggfun=sum),
        ],
    )
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
