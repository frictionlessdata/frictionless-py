from __future__ import annotations
import attrs
import os
from typing import Optional, List
from ...dialect import Control


DEFAULT_FORMATS = ["csv", "tsv", "xlsx", "xls", "jsonl", "ndjson"]
DEFAULT_PER_PAGE = 30


@attrs.define(kw_only=True)
class GithubControl(Control):
    """Github control representation"""

    type = "github"

    # State

    apikey: Optional[str] = os.environ.get("GITHUB_ACCESS_TOKEN", None)
    """The access token to authenticate to the github API. It is required 
    to write files to github repo. For reading, it is optional however using 
    apikey increases access limit from 60 to 5000 requests per hour."""

    basepath: Optional[str] = None
    """Path to write the package and resource files"""

    email: Optional[str] = os.environ.get("GITHUB_EMAIL", None)
    """Should be set explicitly while publishing repositores, if the primary 
    email for the github account is not set to public."""

    formats: Optional[List[str]] = DEFAULT_FORMATS
    """By default it is set to 'csv,xls,xlsx', if specified 
    explicitly it only reads file with given types."""

    name: Optional[str] = os.environ.get("GITHUB_NAME", None)
    """Name of the github user. Should be provided while 
    publishing data, if the name of the user is not set in the github account."""

    order: Optional[str] = None
    """Asc or Desc order in which to retrive the data sorted by 'sort' param."""

    page: Optional[int] = None
    """If specified, only the given page is returned."""

    per_page: Optional[int] = DEFAULT_PER_PAGE
    """No of results per page. Default value is 30."""

    repo: Optional[str] = None
    """Name of the repo to read or write."""

    search: Optional[str] = None
    """Search query containing one or more search keywords and qualifiers to filter the repositories. 
    For example, 'windows+label:bug+language:python'."""

    sort: Optional[str] = None
    """Sorts the result of the query by number of stars, forks, help-wanted-issues or updated. 
    By default the results are sorted by best match in desc order."""

    user: Optional[str] = None
    """username of the github account."""

    filename: Optional[str] = None
    """Custom data package file name while publishing the data. By default it will use 'datapackage.json'."""

    # Metadata

    metadata_profile_patch = {
        "properties": {
            "apikey": {"type": "string"},
            "email": {"type": "string"},
            "formats": {"type": "array"},
            "name": {"type": "string"},
            "order": {"type": "string"},
            "per_page": {"type": "int"},
            "page": {"type": "int"},
            "repo": {"type": "string"},
            "search": {"type": "str"},
            "sort": {"type": "string"},
            "user": {"type": "string"},
            "filename": {"type": "string"},
        },
    }
