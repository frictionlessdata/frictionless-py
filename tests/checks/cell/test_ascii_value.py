from frictionless import validate, checks


# Issues


def test_validate_ascii_value_845():
    report = validate(
        "data/ascii.csv",
        checks=[checks.ascii_value()],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == []


def test_validate_ascii_forbidden_value_845():
    report = validate(
        "data/ascii.csv",
        checks=[checks.ascii_value(forbidden_values=[2])],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, 2, "forbidden-value"],
    ]


def test_validate_ascii_not_valid_845():
    report = validate(
        "data/ascii-notvalid.csv",
        checks=[checks.ascii_value()],
    )
    assert report.flatten(["rowPosition", "fieldPosition", "code"]) == [
        [2, 2, "not-ascii"],
        [2, 3, "not-ascii"],
    ]
