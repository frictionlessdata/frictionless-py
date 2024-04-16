from frictionless import ReportTask

# General


def test_report_task():
    task = ReportTask(
        valid=True,
        name="name",
        type="table",
        place="place",
        labels=["label"],
        stats={"warnings": 0, "errors": 0, "seconds": 1.0},
    )
    assert task.name == "name"
    assert task.type == "table"
    assert task.place == "place"
    assert task.labels == ["label"]
    assert task.stats["warnings"] == 0
    assert task.stats["errors"] == 0
    assert task.stats["seconds"] == 1
