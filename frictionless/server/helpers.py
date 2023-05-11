import re
import stringcase
from slugify.slugify import slugify


def make_id(name: str):
    id = slugify(name)
    id = re.sub(f"[^a-zA-Z0-9]+", "_", name)
    id = stringcase.camelcase(id)
    return id
