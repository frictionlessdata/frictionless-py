from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel


class ZenodoCreator(BaseModel):
    name: str
    affiliation: str
    orcid: Optional[str] = None


class ZenodoMetadata(BaseModel):
    title: str
    description: str
    license: str
    publication_date: str
    upload_type: Literal["dataset"]
    access_right: Literal["open"]
    creators: List[ZenodoCreator]
