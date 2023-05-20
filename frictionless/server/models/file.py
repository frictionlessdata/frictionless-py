from typing import Optional
from pydantic import BaseModel


class File(BaseModel):
    type: str
    path: str
    errors: Optional[int] = None
