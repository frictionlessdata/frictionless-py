import stringcase
from copy import deepcopy
from ..exception import FrictionlessException
from ..pipeline import Pipeline
from ..plugin import Plugin
from .. import helpers
from .. import errors


# Plugin


class DataflowsPlugin(Plugin):
    """Plugin for Dataflows

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.dataflows import DataflowsPlugin`

    """

    def create_pipeline(self, type, *, descriptor):
        if type == "dataflows":
            return DataflowsPipeline(descriptor)


# Pipeline


class DataflowsPipeline(Pipeline):
    """Dataflows Pipeline representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.dataflows import DataflowsPipeline`

    Parameters:
        descriptor (str|dict): pipeline descriptor
        tassk? (str): pipeline tasks

    """

    # Run

    def run_task(self, task):
        dataflows = helpers.import_from_plugin("dataflows", plugin="dataflows")

        # Create flow
        steps = []
        for step in task["steps"]:
            desc = deepcopy(step)
            name = stringcase.snakecase(desc.pop("step", ""))
            func = getattr(dataflows, name, None)
            if func is None:
                note = f"Not supported step type: {name}"
                raise FrictionlessException(errors.TaskError(note=note))
            steps.append(func(**helpers.create_options(desc)))
        flow = dataflows.Flow(*steps)

        # Process flow
        flow.process()
