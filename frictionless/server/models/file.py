from typing import Optional

from pydantic import BaseModel


class File(BaseModel):
    type: str
    path: str
    indexed: Optional[bool] = None
    errorCount: Optional[int] = None
