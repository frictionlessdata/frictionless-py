from __future__ import annotations
from ..resource import Resource


class TextResource(Resource):
    type = "text"
    datatype = "text"


class ArticleResource(TextResource):
    datatype = "article"
