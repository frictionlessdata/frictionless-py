from typing import Optional, List
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IFileItem
from ..router import router


class Props(BaseModel):
    session: Optional[str]


class Result(BaseModel):
    items: List[IFileItem]


@router.post("/file/list")
def server_file_list(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    records = project.database.list_records()
    items = project.list_files()
    for index, item in enumerate(items):
        errorCount = None
        record = next(
            filter(lambda record: record["path"] == item["path"], records), None
        )
        if record:
            errorCount = record.get("errorCount", None)
        items[index] = IFileItem(**{**item, "errorCount": errorCount})
    return Result(items=items)
