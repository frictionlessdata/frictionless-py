from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import Request
from pydantic import BaseModel

from ....exception import FrictionlessException
from ... import models
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    folder: Optional[str]


class Result(BaseModel, extra="forbid"):
    files: List[models.File]


@router.post("/file/list", response_model_exclude_unset=True)
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: support .gitignore
def action(project: Project, props: Optional[Props] = None) -> Result:
    fs = project.filesystem
    db = project.database
    md = project.metadata

    # Index by name
    errors_by_name: Dict[str, int] = {}
    for name, descriptor in db.iter_artifacts(type="measure"):
        errors_by_name[name] = descriptor["errors"]

    # Index by path
    type_by_path: Dict[str, str] = {}
    errors_by_path: Dict[str, int] = {}
    for descriptor in md.iter_documents(type="record"):
        path = descriptor["path"]
        type_by_path[path] = descriptor["type"]
        errors_by_path[path] = errors_by_name.get(descriptor["name"], 0)

    # Get folder
    folder = fs.basepath
    if props and props.folder:
        folder = fs.get_fullpath(props.folder)
        if not folder.is_dir():
            raise FrictionlessException("folder not found")

    # List files
    items: List[models.File] = []
    for root, folders, files in os.walk(folder):
        root = Path(root)
        for file in files:
            if file.startswith("."):
                continue
            path = fs.get_path(root / file)
            item = models.File(path=path, type=type_by_path.get(path, "file"))
            if path in type_by_path:
                item.indexed = True
            if path in errors_by_path:
                item.errorCount = errors_by_path[path]
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
