import os
from typing import List, Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IFileItem
from ...router import router


class Props(BaseModel):
    pass


class Result(BaseModel):
    items: List[IFileItem]


@router.post("/file/list")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Optional[Props] = None) -> Result:
    fs = project.filesystem

    items: List[IFileItem] = []
    for root, folders, files in os.walk(fs.basepath):
        if not fs.is_basepath(root):
            folder = fs.get_secure_relpath(root)
            if fs.is_hidden_path(folder):
                continue
        for file in files:
            if fs.is_hidden_path(file):
                continue
            type = fs.get_filetype(os.path.join(root, file))
            path = fs.get_secure_relpath(os.path.join(root, file))
            item = IFileItem(path=path)
            if type:
                item["type"] = type
            items.append(item)
        for folder in folders:
            if fs.is_hidden_path(folder):
                continue
            path = fs.get_secure_relpath(os.path.join(root, folder))
            items.append(IFileItem(path=path, type="folder"))
    items = list(sorted(items, key=lambda item: item["path"]))

    return Result(items=items)
