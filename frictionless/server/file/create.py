from fastapi import UploadFile
from ..server import server


@server.post("/file/create")
def server_create_file(file: UploadFile):
    print(file)
    return {"filename": file.filename}
