from frictionless import Checklist, checks


# General


def test_checklist():
    checklist = Checklist(checks=[checks.ascii_value()])
    assert checklist.check_codes == ["ascii-value"]
    assert checklist.limit_errors == 1000
    assert checklist.limit_memory == 1000
    assert checklist.keep_original is False
    assert checklist.allow_parallel is False
    assert checklist.scope == [
        "hash-count",
        "byte-count",
        "field-count",
        "row-count",
        "blank-header",
        "extra-label",
        "missing-label",
        "blank-label",
        "duplicate-label",
        "incorrect-label",
        "blank-row",
        "primary-key",
        "foreign-key",
        "extra-cell",
        "missing-cell",
        "type-error",
        "constraint-error",
        "unique-error",
        "ascii-value",
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
    assert checklist.check_codes == ["ascii-value"]
    assert checklist.limit_errors == 100
    assert checklist.limit_memory == 100
    assert checklist.keep_original is True
    assert checklist.allow_parallel is True
    assert checklist.scope.count("ascii-value")
    assert isinstance(checklist.checks[0], checks.ascii_value)
