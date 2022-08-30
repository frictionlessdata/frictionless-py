from __future__ import annotations
from pydantic import BaseModel
from fastapi import HTTPException
from ..exception import FrictionlessException
from ..inquiry import Inquiry
from .server import server


class ValidatePayload(BaseModel):
    inquiry: dict


@server.post("/validate")
def server_validate(payload: ValidatePayload):
    try:
        inquiry = Inquiry.from_descriptor(payload.inquiry)
    except FrictionlessException as exception:
        raise HTTPException(status_code=422, detail=str(exception))
    report = inquiry.validate()
    return dict(report=report.to_descriptor())
