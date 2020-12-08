import pytest
from frictionless import validate, helpers


# General


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_hash():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", checksum={"hash": hash})
    assert report.table["valid"]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_hash_invalid():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", checksum={"hash": "bad"})
    assert report.flatten(["code", "note"]) == [
        ["checksum-error", 'expected hash in md5 is "bad" and actual is "%s"' % hash],
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_hash_md5():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", checksum={"hash": hash})
    assert report.table["valid"]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_hash_md5_invalid():
    hash = "6c2c61dd9b0e9c6876139a449ed87933"
    report = validate("data/table.csv", checksum={"hash": "bad"})
    assert report.flatten(["code", "note"]) == [
        ["checksum-error", 'expected hash in md5 is "bad" and actual is "%s"' % hash],
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_hash_sha1():
    hash = "db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e"
    report = validate("data/table.csv", hashing="sha1", checksum={"hash": hash})
    assert report.table["valid"]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_hash_sha1_invalid():
    hash = "db6ea2f8ff72a9e13e1d70c28ed1c6b42af3bb0e"
    report = validate("data/table.csv", hashing="sha1", checksum={"hash": "bad"})
    assert report.flatten(["code", "note"]) == [
        ["checksum-error", 'expected hash in sha1 is "bad" and actual is "%s"' % hash],
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_hash_sha256():
    hash = "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
    report = validate("data/table.csv", hashing="sha256", checksum={"hash": hash})
    assert report.table["valid"]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_hash_sha256_invalid():
    hash = "a1fd6c5ff3494f697874deeb07f69f8667e903dd94a7bc062dd57550cea26da8"
    report = validate("data/table.csv", hashing="sha256", checksum={"hash": "bad"})
    assert report.flatten(["code", "note"]) == [
        ["checksum-error", 'expected hash in sha256 is "bad" and actual is "%s"' % hash],
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_hash_sha512():
    hash = "d52e3f5f5693894282f023b9985967007d7984292e9abd29dca64454500f27fa45b980132d7b496bc84d336af33aeba6caf7730ec1075d6418d74fb8260de4fd"
    report = validate("data/table.csv", hashing="sha512", checksum={"hash": hash})
    assert report.table["valid"]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_hash_sha512_invalid():
    hash = "d52e3f5f5693894282f023b9985967007d7984292e9abd29dca64454500f27fa45b980132d7b496bc84d336af33aeba6caf7730ec1075d6418d74fb8260de4fd"
    report = validate("data/table.csv", hashing="sha512", checksum={"hash": "bad"})
    assert report.flatten(["code", "note"]) == [
        ["checksum-error", 'expected hash in sha512 is "bad" and actual is "%s"' % hash],
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_bytes():
    report = validate("data/table.csv", checksum={"bytes": 30})
    assert report.table["valid"]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_bytes_invalid():
    report = validate("data/table.csv", checksum={"bytes": 40})
    assert report.table.error.get("rowPosition") is None
    assert report.table.error.get("fieldPosition") is None
    assert report.flatten(["code", "note"]) == [
        ["checksum-error", 'expected bytes count is "40" and actual is "30"'],
    ]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_rows():
    report = validate("data/table.csv", checksum={"rows": 2})
    assert report.table["valid"]


@pytest.mark.skipif(helpers.is_platform("windows"), reason="It doesn't work for Windows")
def test_validate_checksum_rows_invalid():
    report = validate("data/table.csv", checksum={"rows": 3})
    assert report.table.error.get("rowPosition") is None
    assert report.table.error.get("fieldPosition") is None
    assert report.flatten(["code", "note"]) == [
        ["checksum-error", 'expected rows count is "3" and actual is "2"'],
    ]
