import stringcase
from importlib import import_module
from .metadata import Metadata
from . import exceptions
from . import helpers
from . import errors


class Pipeline(Metadata):
    """Pipeline representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Pipeline`

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

    def __init__(self, descriptor=None, *, name=None, type=None, steps=None):
        self.setinitial("name", name)
        self.setinitial("type", type)
        self.setinitial("steps", steps)
        super().__init__(descriptor)

    @Metadata.property
    def name(self):
        """
        Returns:
            str?: pipeline name
        """
        return self.get("name")

    @Metadata.property
    def type(self):
        """
        Returns:
            str?: pipeline type
        """
        return self.get("type")

    @Metadata.property
    def steps(self):
        """
        Returns:
            dict[]?: pipeline steps
        """
        return self.get("steps")

    # Run

    # NOTE: rebase on the plugin system
    def run(self):
        """Run the pipeline"""

        # Check type
        if self.type != "package":
            error = errors.Error(note='For now, the only supported type is "package"')
            raise exceptions.FrictionlessException(error)

        # Import dataflows
        try:
            dataflows = import_module("dataflows")
        except ImportError:
            error = errors.Error(note='Please install "frictionless[dataflows]"')
            raise exceptions.FrictionlessException(error)

        # Create flow
        items = []
        for step in self.steps:
            func = getattr(dataflows, stringcase.lowercase(step["type"]))
            items.append(func(**helpers.create_options(step["spec"])))
        flow = dataflows.Flow(*items)

        # Process flow
        flow.process()

    # Metadata

    metadata_Error = errors.PipelineError
    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["type", "steps"],
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "steps": {
                "type": "array",
                "items": {"type": "object", "required": ["type", "spec"]},
            },
        },
    }
