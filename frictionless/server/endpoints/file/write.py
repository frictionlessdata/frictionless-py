from pydantic import BaseModel
from fastapi import Request, UploadFile, File, Form
from ...project import Project
from ...router import router


# See the signature
class Props(BaseModel):
    pass


class Result(BaseModel):
    path: str


@router.post("/file/write")
async def server_file_write(
    request: Request,
    file: UploadFile = File(),
    path: str = Form(None),
) -> Result:
    project: Project = request.app.get_project()
    bytes = await file.read()
    project.write_file(path, bytes=bytes)
    return Result(path=path)
