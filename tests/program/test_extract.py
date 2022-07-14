import pytest
import json
import yaml
from typer.testing import CliRunner
from frictionless import program, extract, formats, Detector, helpers, Resource, Dialect


runner = CliRunner()


# General


def test_program_extract():
    actual = runner.invoke(program, "extract data/table.csv")
    assert actual.exit_code == 0
    assert actual.stdout.count("table.csv")
    assert actual.stdout.count("id  name")
    assert actual.stdout.count("1  english")
    assert actual.stdout.count("2  中国人")


def test_program_extract_header_rows():
    actual = runner.invoke(program, "extract data/table.csv --json --header-rows '1,2'")
    expect = extract("data/table.csv", dialect=Dialect(header_rows=[1, 2]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_program_extract_header_join():
    actual = runner.invoke(
        program,
        "extract data/table.csv --json --header-rows '1,2' --header-join ':'",
    )
    expect = extract(
        "data/table.csv",
        dialect=Dialect(header_rows=[1, 2], header_join=":"),
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_program_extract_comment_rows():
    actual = runner.invoke(program, "extract data/table.csv --json --comment-rows 1")
    expect = extract("data/table.csv", dialect=Dialect(comment_rows=[1]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_program_extract_schema():
    actual = runner.invoke(
        program,
        "extract data/table.csv --json --schema data/schema.json",
    )
    expect = extract(
        "data/table.csv",
        schema="data/schema.json",
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_program_extract_sync_schema():
    actual = runner.invoke(
        program,
        "extract data/table.csv --json --schema data/schema-reverse.json --schema-sync",
    )
    expect = extract(
        "data/table.csv",
        schema="data/schema.json",
        detector=Detector(schema_sync=True),
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_program_extract_field_type():
    actual = runner.invoke(program, "extract data/table.csv --json --field-type string")
    expect = extract("data/table.csv", detector=Detector(field_type="string"))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_program_extract_field_names():
    actual = runner.invoke(program, "extract data/table.csv --json --field-names 'a,b'")
    expect = extract("data/table.csv", detector=Detector(field_names=["a", "b"]))
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_program_extract_field_missing_values():
    actual = runner.invoke(
        program, "extract data/table.csv --json --field-missing-values 1"
    )
    expect = extract(
        "data/table.csv",
        detector=Detector(field_missing_values=["1"]),
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


def test_program_extract_yaml():
    actual = runner.invoke(program, "extract data/table.csv --json")
    expect = extract("data/table.csv")
    assert actual.exit_code == 0
    assert yaml.safe_load(actual.stdout) == expect


def test_program_extract_json():
    actual = runner.invoke(program, "extract data/table.csv --json")
    expect = extract("data/table.csv")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == expect


@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_program_extract_csv():
    actual = runner.invoke(program, "extract data/table.csv --csv")
    with open("data/table.csv") as file:
        expect = file.read()
    assert actual.exit_code == 0
    assert actual.stdout == expect


@pytest.mark.xfail(reason="Not supported yet")
def test_program_extract_dialect_sheet_option():
    file = "data/sheet2.xls"
    sheet = "Sheet2"
    actual = runner.invoke(program, f"extract {file} --sheet {sheet} --json")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == extract(file, dialect={"sheet": sheet})


@pytest.mark.xfail(reason="Not supported yet")
@pytest.mark.skipif(helpers.is_platform("windows"), reason="Fix on Windows")
def test_program_extract_dialect_table_option_sql(database_url):
    table = "fruits"
    actual = runner.invoke(program, f"extract {database_url} --table {table} --json")
    assert actual.exit_code == 0
    control = formats.SqlControl(table=table)
    with Resource(database_url, control=control) as resource:
        assert json.loads(actual.stdout) == extract(resource)


@pytest.mark.xfail(reason="Not supported yet")
def test_program_extract_dialect_keyed_option():
    file = "data/table.keyed.json"
    keyed = True
    actual = runner.invoke(program, f"extract --path {file} --keyed {keyed} --json")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == extract(path=file, dialect={"keyed": keyed})


@pytest.mark.xfail(reason="Not supported yet")
def test_program_extract_dialect_keys_option():
    file = "data/table.keyed.json"
    actual = runner.invoke(program, f"extract --path {file} --keys 'name,id' --json")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == extract(
        path=file, dialect={"keys": ["name", "id"]}
    )


def test_program_extract_valid_rows():
    actual = runner.invoke(program, "extract data/countries.csv --valid --json")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == [
        {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
        {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
        {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
    ]


def test_program_extract_yaml_valid_rows():
    actual = runner.invoke(program, "extract data/countries.csv --valid --yaml")
    assert actual.exit_code == 0
    with open("data/fixtures/issue-1004/valid-countries.yaml", "r") as stream:
        expect = yaml.safe_load(stream)
    assert yaml.safe_load(actual.stdout) == expect


def test_program_extract_invalid_rows():
    actual = runner.invoke(program, "extract data/countries.csv --invalid --json")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == [
        {"id": 2, "neighbor_id": "3", "name": "France", "population": "n/a"},
        {"id": 5, "neighbor_id": None, "name": None, "population": None},
    ]


def test_program_extract_valid_rows_with_no_valid_rows():
    actual = runner.invoke(program, "extract data/invalid.csv --valid")
    assert actual.exit_code == 0
    assert actual.stdout.count("data: data/invalid.csv")
    assert actual.stdout.count("No valid rows")


def test_program_extract_invalid_rows_with_no_invalid_rows():
    actual = runner.invoke(program, "extract data/capital-valid.csv --invalid")
    assert actual.exit_code == 0
    assert actual.stdout.count("data: data/capital-valid.csv")
    assert actual.stdout.count("No invalid rows")


def test_program_extract_valid_rows_from_datapackage_with_multiple_resources():
    IS_UNIX = not helpers.is_platform("windows")
    path1 = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    path2 = "data/issue-1004-data2.csv" if IS_UNIX else "data\\issue-1004-data2.csv"
    actual = runner.invoke(program, "extract data/issue-1004.package.json --valid --json")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == {
        path1: [
            {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
            {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
            {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
        ],
        path2: [],
    }


def test_program_extract_invalid_rows_from_datapackage_with_multiple_resources():
    IS_UNIX = not helpers.is_platform("windows")
    path1 = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    path2 = "data/issue-1004-data2.csv" if IS_UNIX else "data\\issue-1004-data2.csv"
    actual = runner.invoke(
        program, "extract data/issue-1004.package.json --invalid --json"
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == {
        path1: [
            {"id": 2, "neighbor_id": "3", "name": "France", "population": "n/a"},
            {"id": 5, "neighbor_id": None, "name": None, "population": None},
        ],
        path2: [
            {"id": 1, "name": "english", "country": None, "city": None},
            {"id": 1, "name": "english", "country": None, "city": None},
            {"id": None, "name": None, "country": None, "city": None},
            {"id": 2, "name": "german", "country": 1, "city": 2},
        ],
    }


@pytest.mark.xfail(reason="Not supported yet")
def test_program_extract_valid_rows_extract_dialect_sheet_option():
    actual = runner.invoke(
        program, "extract data/sheet2.xls --sheet Sheet2 --json --valid"
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


@pytest.mark.xfail(reason="Not supported yet")
def test_program_extract_invalid_rows_extract_dialect_sheet_option():
    actual = runner.invoke(
        program, "extract data/sheet2.xls --sheet Sheet2 --json --invalid"
    )
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == []
