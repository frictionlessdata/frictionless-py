import os
from frictionless import Package


# General


def test_erd_mapper_package_to_erd():
    package = Package("data/package-storage.json")

    # Read
    with open("data/fixtures/dot-files/package.dot") as file:
        assert package.to_er_diagram().strip() == file.read().strip()


def test_erd_mapper_package_to_erd_table_names_with_dash(tmpdir):
    # graphviz shows error if the table/field name has "-" so need to
    # wrap names with quotes ""
    package = Package("data/datapackage.json")
    expected_file_path = (
        "data/fixtures/dot-files/package-resource-names-including-dash.dot"
    )
    output_file_path = os.path.join(tmpdir, "output.dot")

    # Read - expected
    with open(expected_file_path) as file:
        expected = file.read()

    # Write
    package.to_er_diagram(output_file_path)

    # Read - output
    with open(output_file_path) as file:
        output = file.read()
    assert expected.strip() == output.strip()
    assert output.count('"number-two"')


def test_erd_mapper_package_to_erd_without_table_relationships(tmpdir):
    package = Package("data/datapackage.json")
    expected_file_path = (
        "data/fixtures/dot-files/package-resource-names-including-dash.dot"
    )
    output_file_path = os.path.join(tmpdir, "output.dot")

    # Read - expected
    with open(expected_file_path) as file:
        expected = file.read()

    # Write
    package.to_er_diagram(output_file_path)

    # Read - soutput
    with open(output_file_path) as file:
        output = file.read()
    assert expected.strip() == output.strip()
    assert output.count("->") == 0
