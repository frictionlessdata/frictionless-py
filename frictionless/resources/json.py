from __future__ import annotations
import json
from typing import Optional, Any, Union
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
        res = target
        if not isinstance(res, Resource):
            res = Resource(target, **options)
            assert isinstance(res, JsonResource)
        data = self.read_json()
        text = helpers.to_yaml(data) if res.format == "yaml" else helpers.to_json(data)
        bytes = text.encode("utf-8")
        assert res.normpath
        helpers.write_file(res.normpath, bytes, mode="wb")
        return res


class JsonschemaResource(JsonResource):
    datatype = "jsonschema"
