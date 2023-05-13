from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import Request, UploadFile, File, Form
from ....exception import FrictionlessException
from ...project import Project
from ...router import router
from .... import helpers


class Props(BaseModel):
    path: str
    bytes: bytes
    folder: Optional[str] = None
    deduplicate: Optional[bool] = None


class Result(BaseModel):
    path: str


# TODO: use streaming?
@router.post("/file/create")
async def endpoint(
    request: Request,
    file: UploadFile = File(),
    name: Optional[str] = Form(None),
    folder: Optional[str] = Form(None),
    deduplicate: Optional[bool] = Form(None),
) -> Result:
    bytes = await file.read()
    name = name or file.filename or "name"
    return action(
        request.app.get_project(),
        Props(path=name, bytes=bytes, folder=folder, deduplicate=deduplicate),
    )


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    # Folder
    if props.folder:
        if not fs.get_fullpath(props.folder).exists():
            raise FrictionlessException("Folder doesn't exist")

    # Target
    target = fs.get_fullpath(props.folder, props.path, deduplicate=props.deduplicate)
    if target.exists():
        raise FrictionlessException("File already exists")

    # Create
    helpers.write_file(str(target), props.bytes, mode="wb")
    path = fs.get_path(target)

    return Result(path=path)
