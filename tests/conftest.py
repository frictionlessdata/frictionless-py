import os
import pytest
import sqlalchemy as sa
from frictionless import platform
from pytest_cov.embed import cleanup_on_sigterm


# TODO: stop using the Bugs section in the tests and split them among themed categories?


# Cleanups


cleanup_on_sigterm()


# Fixtures


@pytest.fixture
def database_url(sqlite_url):
    engine = sa.create_engine(sqlite_url)
    conn = engine.connect()
    conn.execute("CREATE TABLE 'table' (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO 'table' VALUES (1, 'english'), (2, '中国人')")
    conn.execute(
        "CREATE TABLE 'fruits' (uid INTEGER PRIMARY KEY, fruit_name TEXT, calories INTEGER)"
    )
    conn.execute("INSERT INTO 'fruits' VALUES (1, 'Apples', 200), (2, 'Oranges中国人', 350)")
    yield sqlite_url
    conn.close()


@pytest.fixture
def sqlite_url(tmpdir):
    path = str(tmpdir.join("database.db"))
    return "sqlite:///%s" % path


# TODO: create fixture to keep connection to speed up tests?
@pytest.fixture
def postgresql_url():
    url = os.environ.get("POSTGRESQL_URL")
    if not url:
        pytest.skip('Environment varialbe "POSTGRESQL_URL" is not available')
    yield url
    engine = sa.create_engine(url)
    with engine.connect() as conn:
        metadata = sa.MetaData(bind=conn)
        metadata.reflect()
        for table in reversed(metadata.sorted_tables):
            conn.execute(f'DROP TABLE "{table.name}" CASCADE')


# TODO: create fixture to keep connection to speed up tests?
@pytest.fixture
def mysql_url():
    url = os.environ.get("MYSQL_URL")
    if not url:
        pytest.skip('Environment varialbe "MYSQL_URL" is not available')
    yield url
    engine = sa.create_engine(url)
    with engine.connect() as conn:
        metadata = sa.MetaData(bind=conn)
        metadata.reflect()
        conn.execute("DROP VIEW IF EXISTS `view`")
        for table in reversed(metadata.sorted_tables):
            conn.execute(f"DROP TABLE `{table.name}` CASCADE")


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
