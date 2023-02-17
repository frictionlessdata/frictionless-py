import pytest
import sqlite3


@pytest.fixture
def sqlite_max_variable_number():
    # Return SQLite max. variable number limit, set as compile option, or
    # default.
    #
    # Default value for stock SQLite >= 3.32.0
    # (https://www.sqlite.org/limits.html#max_variable_number): 32766
    #
    # Note that distributions *do* customize this e.g. Ubuntu 20.04:
    # MAX_VARIABLE_NUMBER=250000
    conn = sqlite3.connect(":memory:")
    try:
        with conn:
            result = conn.execute("pragma compile_options;").fetchall()
    finally:
        conn.close()
    for item in result:  # type: ignore
        if item[0].startswith("MAX_VARIABLE_NUMBER="):
            return int(item[0].split("=")[-1])
    return 32766
