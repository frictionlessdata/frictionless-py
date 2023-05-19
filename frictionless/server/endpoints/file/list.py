from __future__ import annotations
import os
from pathlib import Path
from typing import List, Optional, Dict
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ... import models


class Props(BaseModel):
    pass


class Result(BaseModel):
    files: List[models.File]


@router.post("/file/list")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: support .gitignore
def action(project: Project, props: Optional[Props] = None) -> Result:
    fs = project.filesystem
    md = project.metadata
    db = project.database

    # Map by id
    errors_by_id: Dict[str, int] = {}
    for id, descriptor in db.iter_artifacts(type="stats"):
        errors_by_id[id] = descriptor["errors"]

    # Map by path
    type_by_path: Dict[str, str] = {}
    errors_by_path: Dict[str, Optional[int]] = {}
    for descriptor in md.iter_documents(type="record"):
        id = descriptor["id"]
        path = descriptor["path"]
        type = descriptor["type"]
        type_by_path[path] = type
        errors_by_path[path] = errors_by_id.get(id, None)

    # List files
    items: List[models.File] = []
    for root, folders, files in os.walk(fs.basepath):
        root = Path(root)
        for file in files:
            if file.startswith("."):
                continue
            path = fs.get_path(root / file)
            item = models.File(
                path=path,
                type=type_by_path.get(path, "file"),
                errors=errors_by_path.get(path, None),
            )
            items.append(item)
        for folder in list(folders):
            if folder.startswith(".") or folder in IGNORED_FOLDERS:
                folders.remove(folder)
                continue
            path = fs.get_path(root / folder)
            item = models.File(path=path, type="folder")
            items.append(item)

    items = list(sorted(items, key=lambda item: item.path))
    return Result(files=items)


IGNORED_FOLDERS = [
    "node_modules",
]
