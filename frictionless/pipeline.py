import stringcase
from importlib import import_module
from .metadata import Metadata
from .resource import Resource
from .package import Package
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

    def __init__(self, descriptor=None, *, name=None, type=None, source=None, steps=None):
        self.setinitial("name", name)
        self.setinitial("type", type)
        self.setinitial("source", source)
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
        return self.get("type", "resource")

    @Metadata.property
    def source(self):
        """
        Returns:
            dict[]?: pipeline source
        """
        return self.get("source")

    @Metadata.property
    def steps(self):
        """
        Returns:
            dict[]?: pipeline steps
        """
        return self.get("steps")

    # Run

    def run(self):
        """Run the pipeline"""
        steps = import_module("frictionless.steps")
        transforms = import_module("frictionless.transform")
        # TODO: it will not work for nested steps like steps.resource_transform
        items = []
        for step in self.steps:
            # TODO: remove nested naming just use "step" prop
            func = getattr(steps, stringcase.snakecase(step["type"]))
            items.append(func(**helpers.create_options(step["spec"])))
        if self.type == "resource":
            source = Resource(self.source)
            return transforms.transform_resource(source, steps=items)
        else:
            source = Package(self.source)
            return transforms.transform_package(source, steps=items)

    # Metadata

    metadata_Error = errors.PipelineError
    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["type", "source", "steps"],
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "source": {"type": "object"},
            "steps": {
                "type": "array",
                "items": {"type": "object", "required": ["type", "spec"]},
            },
        },
    }
