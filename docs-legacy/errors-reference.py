import os
from scripts import docs
from jinja2 import Template
from frictionless import errors


source = os.path.join(docs.SOURCE_DIR, "errors-reference.md")
target_dir = os.path.join(docs.TARGET_DIR, "errors-reference")
target_md = os.path.join(target_dir, "README.md")
with open(source) as file:
    template = Template(file.read())
    Errors = [item for item in vars(errors).values() if hasattr(item, "code")]
    document = template.render(Errors=Errors)
os.makedirs(target_dir, exist_ok=True)
with open(target_md, "wt") as file:
    file.write(document)
