from frictionless import validate, checks


def test_validate_deviated_cell_1066():
    report = validate(
        "data/issue-1066.csv",
        checks=[checks.deviated_cell()],
    )
    assert report.flatten(["code", "note"]) == [
        ["deviated-cell", 'cell at row "35" and field "Gestore" has deviated size']
    ]


def test_validate_deviated_cell_using_descriptor():
    report = validate(
        "data/issue-1066.csv",
        checks=[
            {
                "code": "deviated-cell",
                "ignoreFields": [
                    "Latitudine",
                    "Longitudine",
                ],
                "interval": 3,
            }
        ],
    )
    assert report.flatten(["code", "note"]) == [
        ["deviated-cell", 'cell at row "35" and field "Gestore" has deviated size']
    ]


def test_validate_deviated_cell_not_enough_data():
    source = [
        ["countries"],
        ["UK"],
    ]
    report = validate(
        source,
        checks=[checks.deviated_cell()],
    )
    assert report.flatten(["code", "note"]) == []


def test_validate_deviated_cell_large_cell_size_without_deviation():
    report = validate(
        "data/issue-1066-largecellsize.csv",
        checks=[checks.deviated_cell()],
    )
    assert report.flatten(["code", "note"]) == []


def test_validate_deviated_cell_large_cell_size_with_deviation():
    report = validate(
        "data/issue-1066-largecellsizewithdeviation.csv",
        checks=[checks.deviated_cell()],
    )
    assert report.flatten(["code", "note"]) == [
        ["deviated-cell", 'cell at row "5" and field "Description" has deviated size']
    ]


def test_validate_deviated_cell_small_cell_size():
    report = validate(
        "data/issue-1066-smallcellsize.csv",
        checks=[checks.deviated_cell()],
    )
    assert report.flatten(["code", "note"]) == []


def test_validate_deviated_cell_small_cell_size_with_deviation():
    report = validate(
        "data/issue-1066-smallcellsizewithdeviation.csv",
        checks=[checks.deviated_cell()],
    )
    assert report.flatten(["code", "note"]) == [
        ["deviated-cell", 'cell at row "13" and field "Description" has deviated size']
    ]
