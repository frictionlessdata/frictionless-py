import os

import pytest
import sqlalchemy as sa
from pytest_cov.embed import cleanup_on_sigterm

from frictionless import platform

# TODO: stop using the Bugs section in the tests and split them among themed categories?


# Cleanups


cleanup_on_sigterm()


# Fixtures


@pytest.fixture
def sqlite_url(tmpdir):
    path = str(tmpdir.join("database.db"))
    return "sqlite:///%s" % path


@pytest.fixture
def sqlite_url_data(sqlite_url):
    engine = sa.create_engine(sqlite_url)
    populate_db(engine)
    yield sqlite_url


@pytest.fixture
def duckdb_url(tmpdir):
    path = str(tmpdir.join("database.db"))
    return "duckdb:///%s" % path


@pytest.fixture
def duckdb_url_data(duckdb_url):
    engine = sa.create_engine(duckdb_url)
    populate_db(engine)
    yield duckdb_url


# TODO: create fixture to keep connection to speed up tests?
@pytest.fixture
def postgresql_url():
    url = os.environ.get("POSTGRESQL_URL")
    if not url:
        pytest.skip('Environment varialbe "POSTGRESQL_URL" is not available')
    yield url
    engine = sa.create_engine(url)
    with engine.begin() as conn:
        metadata = sa.MetaData()
        metadata.reflect(conn)
        for table in reversed(metadata.sorted_tables):
            conn.execute(sa.text(f'DROP TABLE "{table.name}" CASCADE'))


@pytest.fixture
def postgresql_url_data(postgresql_url):
    engine = sa.create_engine(postgresql_url)
    populate_db(engine)
    yield postgresql_url


# TODO: create fixture to keep connection to speed up tests?
@pytest.fixture
def mysql_url():
    url = os.environ.get("MYSQL_URL")
    if not url:
        pytest.skip('Environment varialbe "MYSQL_URL" is not available')
    yield url
    engine = sa.create_engine(url)
    with engine.begin() as conn:
        metadata = sa.MetaData()
        metadata.reflect(conn)
        conn.execute(sa.text("DROP VIEW IF EXISTS `view`"))
        for table in reversed(metadata.sorted_tables):
            conn.execute(sa.text(f"DROP TABLE `{table.name}` CASCADE"))


@pytest.fixture
def mysql_url_data(mysql_url):
    engine = sa.create_engine(mysql_url)
    populate_db(engine)
    yield postgresql_url


@pytest.fixture
def google_credentials_path():
    path = os.environ.get("GOOGLE_CREDENTIALS_PATH")
    if not path or not os.path.isfile(path):
        pytest.skip('Environment variable "GOOGLE_CREDENTIALS_PATH" is not available')
    elif platform.type != "linux":
        pytest.skip('Environment variable "GOOGLE_CREDENTIALS_PATH" is Linux only')
    return path


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


@pytest.fixture(scope="module")
def vcr_cassette_dir(request):
    return os.path.join("data", "cassettes")


# Helpers


def populate_db(engine):
    with engine.begin() as conn:
        conn.execute(sa.text('CREATE TABLE "table" (id INTEGER PRIMARY KEY, name TEXT)'))
        conn.execute(sa.text("INSERT INTO \"table\" VALUES (1, 'english'), (2, '中国人')"))
        conn.execute(
            sa.text(
                "CREATE TABLE fruits (uid INTEGER PRIMARY KEY, fruit_name TEXT, calories INTEGER)"
            )
        )
        conn.execute(
            sa.text(
                "INSERT INTO fruits VALUES (1, 'Apples', 200), (2, 'Oranges中国人', 350)"
            )
        )
