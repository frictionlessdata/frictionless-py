from __future__ import annotations
from pydantic import BaseModel


class Model(BaseModel):
    model_config = dict(extra="allow")
