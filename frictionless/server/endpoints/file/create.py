from typing import Optional
from pydantic import BaseModel
from fastapi import Request
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
    path: Optional[str] = Form(None),
    folder: Optional[str] = Form(None),
) -> Result:
    path = path or file.filename or "name"
    bytes = await file.read()
    return action(request.app.get_project(), Props(path=path, folder=folder, bytes=bytes))


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    fullpath = fs.get_fullpath(props.folder, props.path, deduplicate=props.deduplicate)
    if fs.is_existent(fullpath):
        raise FrictionlessException("Folder already exists")
    helpers.write_file(fullpath, props.bytes, mode="wb")
    path = fs.get_relpath(fullpath)

    return Result(path=path)
