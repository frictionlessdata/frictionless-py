from frictionless import Package


# Read


def test_sql_manager_read_package(database_url):
    package = Package(database_url)
    assert len(package.resources) == 2
