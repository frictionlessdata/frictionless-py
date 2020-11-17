import json
import yaml
from typer.testing import CliRunner
from frictionless import program, extract

runner = CliRunner()


# General


def test_extract():
    result = runner.invoke(program, "extract data/table.csv")
    assert result.exit_code == 0
    assert result.stdout.count("data: data/table.csv")
    assert result.stdout.count("id  name")
    assert result.stdout.count("1  english")
    assert result.stdout.count("2  中国人")


def test_extract_header_rows():
    result = runner.invoke(program, "extract data/table.csv --json --header-rows '1,2'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", dialect={"headerRows": [1, 2]}
    )


def test_extract_header_join():
    result = runner.invoke(
        program, "extract data/table.csv --json --header-rows '1,2' --header-join ':'"
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", dialect={"headerRows": [1, 2], "headerJoin": ":"}
    )


def test_extract_pick_fields():
    result = runner.invoke(program, "extract data/table.csv --json --pick-fields 'id'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", query={"pickFields": ["id"]}
    )


def test_extract_skip_fields():
    result = runner.invoke(program, "extract data/table.csv --json --skip-fields 'id'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", query={"skipFields": ["id"]}
    )


def test_extract_limit_fields():
    result = runner.invoke(program, "extract data/table.csv --json --limit-fields 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", query={"limitFields": 1}
    )


def test_extract_offset_fields():
    result = runner.invoke(program, "extract data/table.csv --json --offset-fields 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", query={"offsetFields": 1}
    )


def test_extract_pick_rows():
    result = runner.invoke(program, "extract data/table.csv --json --pick-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract("data/table.csv", query={"pickRows": [1]})


def test_extract_skip_rows():
    result = runner.invoke(program, "extract data/table.csv --json --skip-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract("data/table.csv", query={"skipRows": [1]})


def test_extract_limit_rows():
    result = runner.invoke(program, "extract data/table.csv --json --limit-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract("data/table.csv", query={"limitRows": 1})


def test_extract_offset_rows():
    result = runner.invoke(program, "extract data/table.csv --json --offset-rows 1")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract("data/table.csv", query={"offsetRows": 1})


def test_extract_schema():
    result = runner.invoke(
        program, "extract data/table.csv --json --schema data/schema.json"
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", schema="data/schema.json"
    )


def test_extract_sync_schema():
    result = runner.invoke(
        program,
        "extract data/table.csv --json --schema data/schema-reverse.json --sync-schema",
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", schema="data/schema.json", sync_schema=True
    )


def test_extract_infer_type():
    result = runner.invoke(program, "extract data/table.csv --json --infer-type string")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract("data/table.csv", infer_type="string")


def test_extract_infer_names():
    result = runner.invoke(program, "extract data/table.csv --json --infer-names 'a,b'")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract("data/table.csv", infer_names=["a", "b"])


def test_extract_infer_missing_values():
    result = runner.invoke(
        program, "extract data/table.csv --json --infer-missing-values 1"
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract(
        "data/table.csv", infer_missing_values=["1"]
    )


def test_extract_yaml():
    result = runner.invoke(program, "extract data/table.csv --json")
    assert result.exit_code == 0
    assert yaml.load(result.stdout) == extract("data/table.csv")


def test_extract_json():
    result = runner.invoke(program, "extract data/table.csv --json")
    assert result.exit_code == 0
    assert json.loads(result.stdout) == extract("data/table.csv")


def test_extract_csv():
    result = runner.invoke(program, "extract data/table.csv --csv")
    assert result.exit_code == 0
    with open("data/table.csv") as file:
        assert result.stdout == file.read()
