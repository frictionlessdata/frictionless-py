import stringcase
from importlib import import_module
from ..pipeline import Pipeline
from ..plugin import Plugin
from .. import exceptions
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

    For now, only the `package` type is supported where `steps` should
    conform to the `dataflows`s processors. The File class inherits
    from the Metadata class all the metadata's functionality


    ```python
    pipeline = Pipeline(
        {
            "type": "package",
            "steps": [
                {"type": "load", "spec": {"loadSource": "data/table.csv"}},
                {"type": "set_type", "spec": {"name": "id", "type": "string"}},
                {"type": "dump_to_path", "spec": {"outPath": tmpdir}},
            ],
        }
    )
    pipeline.run()
    ```

    Parameters:
        descriptor (str|dict): pipeline descriptor
        name? (str): pipeline name
        type? (str): pipeline type
        steps? (dict[]): pipeline steps

    """

    # Run

    def run(self):

        # Import dataflows
        try:
            dataflows = import_module("dataflows")
        except ImportError:
            error = errors.Error(note='Please install "frictionless[dataflows]"')
            raise exceptions.FrictionlessException(error)

        # Create flow
        items = []
        for step in self.steps:
            func = getattr(dataflows, stringcase.snakecase(step["type"]))
            items.append(func(**helpers.create_options(step["spec"])))
        flow = dataflows.Flow(*items)

        # Process flow
        flow.process()
