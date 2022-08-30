from fastapi import UploadFile
from ..router import router


@router.post("/file/create")
def server_create_file(file: UploadFile):
    print(file)
    return {"filename": file.filename}
