import stringcase
from copy import deepcopy
from importlib import import_module
from .exception import FrictionlessException
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
                {"step": "load", "loadSource": "data/table.csv"},
                {"step": "set-type", "name": "id", "type": "string"},
                {"step": "dump-to-path", "outPath": tmpdir},
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
        module = import_module("frictionless.steps")
        transforms = import_module("frictionless.transform")
        steps = []
        for step in self.steps:
            desc = deepcopy(step)
            # TODO: we need the same for nested steps like steps.resource_transform
            name = stringcase.snakecase(desc.pop("step", ""))
            func = getattr(module, name, None)
            if func is None:
                note = f"Not supported step type: {name}"
                raise FrictionlessException(errors.Error(note=note))
            steps.append(func(**helpers.create_options(desc)))
        if self.type == "resource":
            source = Resource(self.source)
            return transforms.transform_resource(source, steps=steps)
        else:
            source = Package(self.source)
            return transforms.transform_package(source, steps=steps)

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
