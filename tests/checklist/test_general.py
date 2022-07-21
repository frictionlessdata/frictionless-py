from frictionless import Checklist, checks


# General


def test_checklist():
    checklist = Checklist(checks=[checks.ascii_value()])
    assert checklist.check_types == ["ascii-value"]
    assert checklist.pick_errors == []
    assert checklist.skip_errors == []
    assert checklist.scope == [
        "md5-count",
        "sha256-count",
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
    checklist = Checklist.from_descriptor({"checks": [{"type": "ascii-value"}]})
    assert checklist.check_types == ["ascii-value"]
    assert checklist.pick_errors == []
    assert checklist.skip_errors == []
    assert checklist.scope.count("ascii-value")
    assert isinstance(checklist.checks[0], checks.ascii_value)


def test_checklist_pick_errors():
    checklist = Checklist(pick_errors=["sha256-count", "byte-count"])
    assert checklist.scope == [
        "sha256-count",
        "byte-count",
    ]


def test_checklist_skip_errors():
    checklist = Checklist(skip_errors=["md5-count", "sha256-count", "byte-count"])
    assert checklist.scope == [
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
    ]


def test_checklist_pick_errors_and_skip_errors():
    checklist = Checklist(
        pick_errors=["sha256-count", "byte-count"],
        skip_errors=["byte-count"],
    )
    assert checklist.scope == [
        "sha256-count",
    ]


def test_checklist_pick_errors_tag():
    checklist = Checklist(pick_errors=["#cell"])
    assert checklist.scope == [
        "extra-cell",
        "missing-cell",
        "type-error",
        "constraint-error",
        "unique-error",
    ]


def test_checklist_skip_errors_tag():
    checklist = Checklist(skip_errors=["#row"])
    assert checklist.scope == [
        "md5-count",
        "sha256-count",
        "byte-count",
        "field-count",
        "row-count",
        "blank-header",
        "extra-label",
        "missing-label",
        "blank-label",
        "duplicate-label",
        "incorrect-label",
    ]
