from __future__ import annotations
import json
from typing import Optional, Any
from ..resource import Resource
from .. import helpers


class JsonResource(Resource):
    type = "json"
    datatype = "json"

    # Read

    # TODO: support yaml?
    def read_data(self, *, size: Optional[int] = None) -> Any:
        """Read data into memory

        Returns:
            any: resource data
        """
        if self.data is not None:
            return self.data
        with helpers.ensure_open(self):
            text = self.read_text(size=size)
            data = json.loads(text)
            return data


class JsonschemaResource(JsonResource):
    datatype = "jsonschema"
