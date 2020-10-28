from importlib import import_module
from .metadata import Metadata
from .resource import Resource
from .package import Package
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

    def run(self):
        """Run the pipeline"""
        raise NotImplementedError()

    # Metadata

    metadata_Error = errors.PipelineError
    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["type", "source", "steps"],
        "properties": {
            "name": {"type": "string"},
            "type": {"type": "string"},
            "steps": {
                "type": "array",
                "items": {"type": "object", "required": ["type", "spec"]},
            },
        },
    }


class ResourcePipeline(Pipeline):
    def __init__(self, descriptor=None, *, name=None, type=None, source=None, steps=None):
        self.setinitial("source", source)
        super().__init__(descriptor, name=name, type=type, steps=steps)

    @Metadata.property
    def source(self):
        """
        Returns:
            dict[]?: pipeline source
        """
        return self.get("source")

    # Run

    def run(self):
        """Run the pipeline"""
        transforms = import_module("frictionless.transform")
        source = Resource(self.source)
        target = transforms.transform_resource(source, steps=self.steps)
        return target

    # Metadata

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


class PackagePipeline(Pipeline):
    def __init__(self, descriptor=None, *, name=None, type=None, source=None, steps=None):
        self.setinitial("source", source)
        super().__init__(descriptor, name=name, type=type, steps=steps)

    @Metadata.property
    def source(self):
        """
        Returns:
            dict[]?: pipeline source
        """
        return self.get("source")

    # Run

    def run(self):
        """Run the pipeline"""
        transforms = import_module("frictionless.transform")
        source = Package(self.source)
        target = transforms.transform_package(source, steps=self.steps)
        return target

    # Metadata

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
