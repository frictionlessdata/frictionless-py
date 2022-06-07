from frictionless import Checklist, checks


# General


def test_checklist():
    checklist = Checklist(checks=[checks.ascii_value()])
    assert checklist.check_codes == ["baseline", "ascii-value"]
    assert checklist.limit_errors == 1000
    assert checklist.limit_memory == 1000
    assert checklist.keep_original is False
    assert checklist.allow_parallel is False
    assert checklist.scope == [
        "hash-count-error",
        "byte-count-error",
        "field-count-error",
        "row-count-error",
        "blank-header",
        "extra-label",
        "missing-label",
        "blank-label",
        "duplicate-label",
        "incorrect-label",
        "blank-row",
        "primary-key-error",
        "foreign-key-error",
        "extra-cell",
        "missing-cell",
        "type-error",
        "constraint-error",
        "unique-error",
        "non-ascii",
    ]


def test_checklist_from_descriptor():
    checklist = Checklist(
        {
            "checks": [{"code": "ascii-value"}],
            "limitErrors": 100,
            "limitMemory": 100,
            "keepOriginal": True,
            "allowParallel": True,
        }
    )
    assert checklist.check_codes == ["baseline", "ascii-value"]
    assert checklist.limit_errors == 100
    assert checklist.limit_memory == 100
    assert checklist.keep_original is True
    assert checklist.allow_parallel is True
    assert checklist.scope.count("non-ascii")
    assert isinstance(checklist.checks[1], checks.ascii_value)
