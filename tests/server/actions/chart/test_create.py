from frictionless.server import Project
from frictionless.server.actions import chart


def test_chart_create(tmpdir):
    project = Project(tmpdir)
    result = chart.create.action(project, chart.create.Props())
    assert result.path == "chart.json"
