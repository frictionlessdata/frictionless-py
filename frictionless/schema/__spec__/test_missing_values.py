import pytest

from frictionless.schema.missing_values import MissingValues

# Read / query

READ_CASES = [
    # name, descriptor, value_strings, contains, not_contains, representation
    (
        "string-form",
        ["", "NA", "N/A"],
        ["", "NA", "N/A"],
        ["", "NA", "N/A"],
        ["x", "-"],
        "",
    ),
    (
        "object-form",
        [{"value": "-99", "label": "REFUSED"}, {"value": "", "label": "OMITTED"}],
        ["-99", ""],
        ["-99", ""],
        ["x", "NA"],
        "-99",
    ),
    (
        "object-without-label",
        [{"value": "-"}],
        ["-"],
        ["-"],
        ["", "x"],
        "-",
    ),
    (
        # empty: no value converts to null, and the representation falls back
        # to the spec default missing value ("")
        "empty",
        [],
        [],
        [],
        ["", "x"],
        "",
    ),
]


@pytest.mark.parametrize(
    "name, descriptor, value_strings, contains, not_contains, representation",
    READ_CASES,
    ids=[case[0] for case in READ_CASES],
)
def test_missing_values_query(
    name, descriptor, value_strings, contains, not_contains, representation
):
    mv = MissingValues.from_descriptor(descriptor)
    assert mv.value_strings() == value_strings
    for value in contains:
        assert value in mv
    for value in not_contains:
        assert value not in mv
    assert mv.representation == representation


# List-like interface (backward compatibility: consumers read List[str])

LIST_LIKE_CASES = [
    ("string-form", ["", "NA", "N/A"], ["", "NA", "N/A"]),
    (
        "object-form",
        [{"value": "-99", "label": "REFUSED"}, {"value": "", "label": "OMITTED"}],
        ["-99", ""],
    ),
    ("empty", [], []),
]


@pytest.mark.parametrize(
    "name, descriptor, expected",
    LIST_LIKE_CASES,
    ids=[case[0] for case in LIST_LIKE_CASES],
)
def test_missing_values_list_like(name, descriptor, expected):
    mv = MissingValues.from_descriptor(descriptor)
    assert mv == expected
    assert list(mv) == expected
    assert len(mv) == len(expected)
    for index, value in enumerate(expected):
        assert mv[index] == value


# Serialization (lossless round-trip)

ROUNDTRIP_CASES = [
    ("string-form", ["", "NA"]),
    ("object-form", [{"value": "-99", "label": "REFUSED"}]),
    ("object-without-label", [{"value": "-"}]),
    ("empty", []),
]


@pytest.mark.parametrize(
    "name, descriptor",
    ROUNDTRIP_CASES,
    ids=[case[0] for case in ROUNDTRIP_CASES],
)
def test_missing_values_roundtrip(name, descriptor):
    mv = MissingValues.from_descriptor(descriptor)
    assert mv.to_descriptor() == descriptor
