import re
import stringcase
from slugify.slugify import slugify


def make_id(name: str):
    ident = slugify(name)
    ident = re.sub(f"[^a-zA-Z0-9]+", "_", name)
    ident = stringcase.camelcase(ident)
    return ident
