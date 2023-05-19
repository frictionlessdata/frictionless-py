from __future__ import annotations
import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ... import models


class Props(BaseModel):
    pass


class Result(BaseModel):
    items: List[models.FileItem]


@router.post("/file/list")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: support .gitignore
def action(project: Project, props: Optional[Props] = None) -> Result:
    fs = project.filesystem

    # List
    items: List[models.FileItem] = []
    for root, folders, files in os.walk(fs.basepath):
        root = Path(root)
        for file in files:
            if file.startswith("."):
                continue
            path = fs.get_path(root / file)
            item = models.FileItem(path=path, type="file")
            items.append(item)
        for folder in list(folders):
            if folder.startswith(".") or folder in IGNORED_FOLDERS:
                folders.remove(folder)
                continue
            path = fs.get_path(root / folder)
            item = models.FileItem(path=path, type="folder")
            items.append(item)

    items = list(sorted(items, key=lambda item: item.path))
    return Result(items=items)


IGNORED_FOLDERS = [
    "node_modules",
]
