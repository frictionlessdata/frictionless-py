from frictionless import validate, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_validate_stats_hash():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", stats={"hash": hash})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_hash_invalid():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", stats={"hash": "bad"})
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            ["hash-count-error", 'expected md5 is "bad" and actual is "%s"' % hash],
        ]


def test_validate_stats_hash_md5():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", stats={"hash": hash})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_hash_md5_invalid():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", stats={"hash": "bad"})
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            ["hash-count-error", 'expected md5 is "bad" and actual is "%s"' % hash],
        ]


def test_validate_stats_hash_sha1():
    hash = "db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e"
    report = validate("data/table.csv", hashing="sha1", stats={"hash": hash})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_hash_sha1_invalid():
    hash = "db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e"
    report = validate("data/table.csv", hashing="sha1", stats={"hash": "bad"})
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            ["hash-count-error", 'expected sha1 is "bad" and actual is "%s"' % hash],
        ]


def test_validate_stats_hash_sha256():
    hash = "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
    report = validate("data/table.csv", hashing="sha256", stats={"hash": hash})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_hash_sha256_invalid():
    hash = "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
    report = validate("data/table.csv", hashing="sha256", stats={"hash": "bad"})
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            [
                "hash-count-error",
                'expected sha256 is "bad" and actual is "%s"' % hash,
            ],
        ]


def test_validate_stats_hash_sha512():
    hash = "d52e3f5f5693894282f023b9985967007d7984292e9abd29dca64454500f27fa45b980132d7b496bc84d336af33aeba6caf7730ec1075d6418d74fb8260de4fd"
    report = validate("data/table.csv", hashing="sha512", stats={"hash": hash})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_hash_sha512_invalid():
    hash = "d52e3f5f5693894282f023b9985967007d7984292e9abd29dca64454500f27fa45b980132d7b496bc84d336af33aeba6caf7730ec1075d6418d74fb8260de4fd"
    report = validate("data/table.csv", hashing="sha512", stats={"hash": "bad"})
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            [
                "hash-count-error",
                'expected sha512 is "bad" and actual is "%s"' % hash,
            ],
        ]


def test_validate_stats_bytes():
    report = validate("data/table.csv", stats={"bytes": 30})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_bytes_invalid():
    report = validate("data/table.csv", stats={"bytes": 40})
    assert report.task.error.get("rowPosition") is None
    assert report.task.error.get("fieldPosition") is None
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            ["byte-count-error", 'expected is "40" and actual is "30"'],
        ]


def test_validate_stats_rows():
    report = validate("data/table.csv", stats={"rows": 2})
    if IS_UNIX:
        assert report.task.valid


def test_validate_stats_rows_invalid():
    report = validate("data/table.csv", stats={"rows": 3})
    assert report.task.error.get("rowPosition") is None
    assert report.task.error.get("fieldPosition") is None
    if IS_UNIX:
        assert report.flatten(["code", "note"]) == [
            ["row-count-error", 'expected is "3" and actual is "2"'],
        ]
