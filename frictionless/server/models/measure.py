from pydantic import BaseModel


class Measure(BaseModel):
    errors: int
