from frictionless import ReportTask


# General


def test_report_task():
    task = ReportTask(name="name", path="path", errors=[])
    assert task.name == "name"
    assert task.path == "path"
