from frictionless import validate, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_encoding():
    report = validate("data/table.csv", encoding="utf-8")
    assert report.valid


def test_validate_encoding_invalid():
    report = validate("data/latin1.csv", encoding="utf-8")
    assert not report.valid
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            [
                "encoding-error",
                "'utf-8' codec can't decode byte 0xa9 in position 20: invalid start byte",
            ],
        ]
