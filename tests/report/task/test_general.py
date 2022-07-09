from frictionless import ReportTask


# General


def test_report_task():
    task = ReportTask(
        valid=True,
        name="name",
        type="table",
        place="place",
        stats={"time": 1},
    )
    assert task.name == "name"
    assert task.type == "table"
    assert task.place == "place"
    assert task.stats == {"time": 1}
