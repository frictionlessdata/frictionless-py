from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel


class ZenodoCreator(BaseModel):
    name: str
    affiliation: Optional[str] = None
    orcid: Optional[str] = None


class ZenodoMetadata(BaseModel):
    title: str
    description: str
    publication_date: str
    license: Optional[str] = None
    upload_type: Literal["dataset"] = "dataset"
    access_right: Literal["open"] = "open"
    creators: List[ZenodoCreator] = []
