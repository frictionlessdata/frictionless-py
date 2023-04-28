from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from fastapi import Request, UploadFile, File, Form
from ...project import Project
from ...router import router
from .... import helpers


# See the signature
class Props(BaseModel):
    name: str
    folder: Optional[str]
    bytes: bytes


class Result(BaseModel):
    path: str


# TODO: use streaming?
@router.post("/file/create")
async def endpoint(
    request: Request,
    file: UploadFile = File(),
    folder: Optional[str] = Form(None),
) -> Result:
    name = file.filename or "name"
    bytes = await file.read()
    return action(request.app.get_project(), Props(name=name, folder=folder, bytes=bytes))


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    assert fs.is_filename(props.name)
    folder = props.folder
    if folder:
        folder = fs.get_secure_fullpath(folder)
        assert fs.is_folder(folder)
    fullpath = fs.get_secure_fullpath(folder, props.name, deduplicate=True)
    helpers.write_file(fullpath, bytes, mode="wb")
    path = fs.get_secure_relpath(fullpath)

    return Result(path=path)
