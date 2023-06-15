from __future__ import annotations
import json
from typing import Optional, Any, Union
from ..exception import FrictionlessException
from ..platform import platform
from ..resource import Resource
from .. import helpers


# TODO: support "resource.jsonSchema" (jsonschema validation)
class JsonResource(Resource):
    type = "json"
    datatype = "json"

    # Read

    # TODO: rebase on using loader
    def read_json(self) -> Any:
        """Read json data into memory

        Returns:
            any: json data
        """
        if self.data is not None:
            return self.data
        with helpers.ensure_open(self):
            text = self.read_text()
            return (
                platform.yaml.safe_load(text)
                if self.format == "yaml"
                else json.loads(text)
            )

    # Write

    # TODO: rebase on using loader
    def write_json(
        self, target: Optional[Union[JsonResource, Any]] = None, **options: Any
    ):
        """Write json data to the target"""
        resource = target
        if not isinstance(resource, Resource):
            resource = Resource(target, **options)
        if not isinstance(resource, JsonResource):
            raise FrictionlessException("target must be a json resource")
        data = self.read_json()
        dump = helpers.to_yaml if resource.format == "yaml" else helpers.to_json
        bytes = dump(data).encode("utf-8")
        assert resource.normpath
        helpers.write_file(resource.normpath, bytes, mode="wb")
        return resource


class JsonschemaResource(JsonResource):
    datatype = "jsonschema"
