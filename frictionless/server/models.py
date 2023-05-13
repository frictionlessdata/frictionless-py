from pydantic import BaseModel


class Stats(BaseModel):
    errors: int
