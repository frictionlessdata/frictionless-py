from frictionless import validate, checks


# Issues


def test_validate_outlier_value_1066():
    report = validate(
        "data/issue-1066.csv", checks=[checks.outlier_value(field_name="Gestore")]
    )
    assert report.flatten(["code", "note"]) == [
        [
            "outlier-value",
            'value in row at position "35" and field "Gestore" is deviated',
        ]
    ]
