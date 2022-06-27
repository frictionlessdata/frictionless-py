from frictionless import ReportTask


# General


def test_report_task():
    task = ReportTask(
        valid=True,
        name="name",
        place="place",
        tabular=True,
        stats={"time": 1},
    )
    assert task.name == "name"
    assert task.place == "place"
    assert task.tabular is True
    assert task.stats == {"time": 1}
