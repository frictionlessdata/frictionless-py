from __future__ import annotations

from .json import JsonResource


class ViewResource(JsonResource):
    type = "view"
    datatype = "view"
