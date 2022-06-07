from frictionless import Resource, Checklist, checks


# General


def test_validate_deviated_cell_1066():
    resource = Resource("data/issue-1066.csv")
    report = resource.validate(checks=[checks.deviated_cell()])
    assert report.flatten(["code", "note"]) == [
        ["deviated-cell", 'cell at row "35" and field "Gestore" has deviated size']
    ]


def test_validate_deviated_cell_using_descriptor():
    resource = Resource("data/issue-1066.csv")
    checklist = Checklist(
        {
            "checks": [
                {
                    "code": "deviated-cell",
                    "ignoreFields": [
                        "Latitudine",
                        "Longitudine",
                    ],
                    "interval": 3,
                }
            ]
        }
    )
    report = resource.validate(checklist)
    assert report.flatten(["code", "note"]) == [
        ["deviated-cell", 'cell at row "35" and field "Gestore" has deviated size']
    ]


def test_validate_deviated_cell_not_enough_data():
    resource = Resource(
        [
            ["countries"],
            ["UK"],
        ]
    )
    report = resource.validate(checks=[checks.deviated_cell()])
    assert report.flatten(["code", "note"]) == []


def test_validate_deviated_cell_large_cell_size_without_deviation():
    resource = Resource("data/issue-1066-largecellsize.csv")
    report = resource.validate(checks=[checks.deviated_cell()])
    assert report.flatten(["code", "note"]) == []


def test_validate_deviated_cell_large_cell_size_with_deviation():
    resource = Resource("data/issue-1066-largecellsizewithdeviation.csv")
    report = resource.validate(checks=[checks.deviated_cell()])
    assert report.flatten(["code", "note"]) == [
        ["deviated-cell", 'cell at row "5" and field "Description" has deviated size']
    ]


def test_validate_deviated_cell_small_cell_size():
    resource = Resource("data/issue-1066-smallcellsize.csv")
    report = resource.validate(checks=[checks.deviated_cell()])
    assert report.flatten(["code", "note"]) == []


def test_validate_deviated_cell_small_cell_size_with_deviation():
    resource = Resource("data/issue-1066-smallcellsizewithdeviation.csv")
    report = resource.validate(checks=[checks.deviated_cell()])
    assert report.flatten(["code", "note"]) == [
        ["deviated-cell", 'cell at row "13" and field "Description" has deviated size']
    ]
