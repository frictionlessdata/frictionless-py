import os
from pathlib import Path
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

    # List
    items: List[IFileItem] = []
    for root, folders, files in os.walk(fs.folder):
        root = Path(root)
        for file in files:
            if file.startswith("."):
                continue
            path = fs.get_path(root / file)
            items.append({"path": path, "type": "file"})
        for folder in list(folders):
            if folder.startswith(".") or folder in IGNORED_FOLDERS:
                folders.remove(folder)
                continue
            path = fs.get_path(root / folder)
            items.append({"path": folder, "type": "folder"})

    items = list(sorted(items, key=lambda item: item["path"]))
    return Result(items=items)


IGNORED_FOLDERS = [
    "node_modules",
]
