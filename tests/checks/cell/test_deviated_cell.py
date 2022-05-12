from frictionless import validate, checks


# Issues


def test_validate_deviated_cell_1066():
    report = validate(
        "data/issue-1066.csv",
        checks=[
            checks.deviated_cell(
                ignore_fields=[
                    "Bandiera",
                    "Tipo Impianto",
                    "Nome Impianto",
                    "Indirizzo",
                    "Comune",
                    "Provincia",
                    "Latitudine",
                    "Longitudine",
                ]
            )
        ],
    )
    assert report.flatten(["code", "note"]) == [
        ["deviated-cell", 'cell at row "35" and field "Gestore" has deviated size']
    ]
