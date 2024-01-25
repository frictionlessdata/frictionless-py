from petl import util

from frictionless.resources import TableResource


def __assert_nth_row(it, n, expected):
    """
    A helper function to assert that the nth row of an iterator is as expected.
    """
    for _ in range(n - 1):
        next(it)
    assert next(it) == expected


def test_to_petl_gives_valid_table():
    resource = TableResource("data/table.csv")
    table = resource.to_petl()
    assert util.header(table) == ("id", "name")


def test_to_petl_is_iterable():
    resource = TableResource("data/table.csv")
    table = resource.to_petl()
    it = iter(table)
    assert next(it) == ["id", "name"]
    assert next(it) == ["1", "english"]
    assert next(it) == ["2", "中国人"]


def test_to_petl_iterators_are_independent():
    resource = TableResource("data/table.csv")
    table = resource.to_petl()
    it1 = iter(table)
    it2 = iter(table)

    # Start reading from it1
    assert next(it1) == ["id", "name"]
    assert next(it1) == ["1", "english"]

    # Check it2 now reads from the start again
    assert next(it2) == ["id", "name"]
    assert next(it2) == ["1", "english"]
    assert next(it2) == ["2", "中国人"]

    # Check it1 is still reading from where it left off
    assert next(it1) == ["2", "中国人"]


def test_to_petl_iterators_have_independent_lifetime():
    resource = TableResource("data/table-1MB.csv")
    table = resource.to_petl()
    it1 = iter(table)

    # Assert the 101st row is as expected.
    # Need to go that far to get past the buffer that is loaded on open()/__enter__
    # and start reading from the file (as the file is closed by close()/__exit__,
    # but the buffer is not, so you would get away with incorrectly closing the
    # resource if you remain within the buffer).
    # See #1622 for more.
    __assert_nth_row(
        it1,
        101,
        [
            "ahltic",
            "22354",
            "428.17",
            "382.54",
            "false",
            "1926-09-15T01:15:27Z",
            "1956-04-14",
            "08:20:13",
            "4,5",
            '{"x":1,"y":7}',
        ],
    )

    # Make a local function to give it2 a different scope
    def read_from_it2():
        it2 = iter(table)
        __assert_nth_row(
            it2,
            101,
            [
                "ahltic",
                "22354",
                "428.17",
                "382.54",
                "false",
                "1926-09-15T01:15:27Z",
                "1956-04-14",
                "08:20:13",
                "4,5",
                '{"x":1,"y":7}',
            ],
        )

    # Read from it2 within the nested function scope
    read_from_it2()

    # Check we can stil read from it1 from where we left off
    # Prior to the fix for #1622 this would throw an exception: "ValueError: I/O operation on closed file."
    __assert_nth_row(
        it1,
        101,
        [
            "tlbmv8",
            "91378",
            "101.19",
            "832.96",
            "false",
            "1983-02-26T12:44:52Z",
            "1960-08-28",
            "04:44:23",
            "5,6",
            '{"x":9,"y":4}',
        ],
    )
