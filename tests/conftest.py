import pytest
import sqlite3
from pytest_cov.embed import cleanup_on_sigterm


# Cleanups


cleanup_on_sigterm()


# Fixtures


@pytest.fixture
def database_url(tmpdir):
    path = str(tmpdir.join("database.db"))
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE 'table' (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO 'table' VALUES (1, 'english'), (2, '中国人')")
    conn.commit()
    yield "sqlite:///%s" % path
    conn.close()


# TODO: create the same for other databases
@pytest.fixture
def sqlite_url(tmpdir):
    path = str(tmpdir.join("database.db"))
    return "sqlite:///%s" % path


# Settings


def pytest_addoption(parser):
    parser.addoption(
        "--ci",
        action="store_true",
        dest="ci",
        default=False,
        help="enable integrational tests",
    )


def pytest_configure(config):
    if not config.option.ci:
        expr = getattr(config.option, "markexpr")
        setattr(config.option, "markexpr", "{expr} and not ci" if expr else "not ci")
