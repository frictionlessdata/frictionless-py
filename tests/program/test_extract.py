from frictionless.plugins.sql import SqlDialect
import json
import yaml
from typer.testing import CliRunner
from frictionless import program, extract, Detector, helpers, Resource

runner = CliRunner()
IS_UNIX = not helpers.is_platform("windows")


# General


def test_program_extract():
    result = runner.invoke(program, "extract data/table.csv")
    assert result.exit_code == 0
    assert result.stdout.count("table.csv")
    assert result.stdout.count("id  name")
    assert result.stdout.count("1  english")
    assert result.stdout.count("2  中国人")


def test_program_extract_header_rows():
    result = runner.invoke(program, "extract data/table.csv --json --header-rows '1,2'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", layout={"headerRows": [1, 2]}
    )


def test_program_extract_header_join():
    result = runner.invoke(
        program, "extract data/table.csv --json --header-rows '1,2' --header-join ':'"
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", layout={"headerRows": [1, 2], "headerJoin": ":"}
    )


def test_program_extract_pick_fields():
    result = runner.invoke(program, "extract data/table.csv --json --pick-fields 'id'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", layout={"pickFields": ["id"]}
    )


def test_program_extract_skip_fields():
    result = runner.invoke(program, "extract data/table.csv --json --skip-fields 'id'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", layout={"skipFields": ["id"]}
    )


def test_program_extract_limit_fields():
    result = runner.invoke(program, "extract data/table.csv --json --limit-fields 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", layout={"limitFields": 1}
    )


def test_program_extract_offset_fields():
    result = runner.invoke(program, "extract data/table.csv --json --offset-fields 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", layout={"offsetFields": 1}
    )


def test_program_extract_pick_rows():
    result = runner.invoke(program, "extract data/table.csv --json --pick-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", layout={"pickRows": [1]}
    )


def test_program_extract_skip_rows():
    result = runner.invoke(program, "extract data/table.csv --json --skip-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", layout={"skipRows": [1]}
    )


def test_program_extract_limit_rows():
    result = runner.invoke(program, "extract data/table.csv --json --limit-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract("data/table.csv", layout={"limitRows": 1})


def test_program_extract_offset_rows():
    result = runner.invoke(program, "extract data/table.csv --json --offset-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", layout={"offsetRows": 1}
    )


def test_program_extract_schema():
    result = runner.invoke(
        program, "extract data/table.csv --json --schema data/schema.json"
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", schema="data/schema.json"
    )


def test_program_extract_sync_schema():
    result = runner.invoke(
        program,
        "extract data/table.csv --json --schema data/schema-reverse.json --schema-sync",
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", schema="data/schema.json", detector=Detector(schema_sync=True)
    )


def test_program_extract_field_type():
    result = runner.invoke(program, "extract data/table.csv --json --field-type string")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", detector=Detector(field_type="string")
    )


def test_program_extract_field_names():
    result = runner.invoke(program, "extract data/table.csv --json --field-names 'a,b'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", detector=Detector(field_names=["a", "b"])
    )


def test_program_extract_field_missing_values():
    result = runner.invoke(
        program, "extract data/table.csv --json --field-missing-values 1"
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", detector=Detector(field_missing_values=["1"])
    )


def test_program_extract_yaml():
    result = runner.invoke(program, "extract data/table.csv --json")
    assert result.exit_code == 0
    assert yaml.safe_load(result.stdout) == extract("data/table.csv")


def test_program_extract_json():
    result = runner.invoke(program, "extract data/table.csv --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract("data/table.csv")


def test_program_extract_csv():
    result = runner.invoke(program, "extract data/table.csv --csv")
    assert result.exit_code == 0
    if IS_UNIX:
        with open("data/table.csv") as file:
            assert result.stdout == file.read()


def test_program_extract_dialect_sheet_option():
    file = "data/sheet2.xls"
    sheet = "Sheet2"
    result = runner.invoke(program, f"extract {file} --sheet {sheet} --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(file, dialect={"sheet": sheet})


def test_program_extract_dialect_table_option_sql(database_url):
    table = "fruits"
    result = runner.invoke(program, f"extract {database_url} --table {table} --json")
    if IS_UNIX:
        assert result.exit_code == 0
        dialect = SqlDialect(table=table)
        with Resource(database_url, dialect=dialect) as resource:
            assert json.loads(result.stdout) == extract(resource)


def test_program_extract_dialect_keyed_option():
    file = "data/table.keyed.json"
    keyed = True
    result = runner.invoke(program, f"extract --path {file} --keyed {keyed} --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(path=file, dialect={"keyed": keyed})


def test_program_extract_dialect_keys_option():
    file = "data/table.keyed.json"
    result = runner.invoke(program, f"extract --path {file} --keys 'name,id' --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        path=file, dialect={"keys": ["name", "id"]}
    )


def test_program_extract_valid_rows_1004():
    result = runner.invoke(program, "extract data/countries.csv --valid --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == [
        {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
        {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
        {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
    ]


def test_program_extract_yaml_valid_rows_1004():
    result = runner.invoke(program, "extract data/countries.csv --valid --yaml")
    assert result.exit_code == 0
    with open("data/fixtures/issue-1004/valid-countries.yaml", "r") as stream:
        expected = yaml.safe_load(stream)
    assert yaml.safe_load(result.stdout) == expected


def test_program_extract_invalid_rows_1004():
    result = runner.invoke(program, "extract data/countries.csv --invalid --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == [
        {"id": 2, "neighbor_id": "3", "name": "France", "population": "n/a"},
        {"id": 5, "neighbor_id": None, "name": None, "population": None},
    ]


def test_program_extract_valid_rows_with_no_valid_rows_1004():
    result = runner.invoke(program, "extract data/invalid.csv --valid")
    assert result.exit_code == 0
    assert result.stdout.count("data: data/invalid.csv") and result.stdout.count(
        "No valid rows"
    )


def test_program_extract_invalid_rows_with_no_invalid_rows_1004():
    result = runner.invoke(program, "extract data/capital-valid.csv --invalid")
    assert result.exit_code == 0
    assert result.stdout.count("data: data/capital-valid.csv") and result.stdout.count(
        "No invalid rows"
    )


def test_program_extract_valid_rows_from_datapackage_with_multiple_resources_1004():
    path1 = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    path2 = "data/issue-1004-data2.csv" if IS_UNIX else "data\\issue-1004-data2.csv"
    result = runner.invoke(program, "extract data/issue-1004.package.json --valid --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        path1: [
            {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
            {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
            {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
        ],
        path2: [],
    }


def test_program_extract_invalid_rows_from_datapackage_with_multiple_resources_1004():
    path1 = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    path2 = "data/issue-1004-data2.csv" if IS_UNIX else "data\\issue-1004-data2.csv"
    result = runner.invoke(
        program, "extract data/issue-1004.package.json --invalid --json"
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
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


def test_program_extract_valid_rows_extract_dialect_sheet_option():
    result = runner.invoke(
        program, "extract data/sheet2.xls --sheet Sheet2 --json --valid"
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_program_extract_invalid_rows_extract_dialect_sheet_option():
    result = runner.invoke(
        program, "extract data/sheet2.xls --sheet Sheet2 --json --invalid"
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == []
