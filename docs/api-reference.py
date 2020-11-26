import os
import re
from subprocess import check_output


TARGET_DIR = os.environ["TARGET_DIR"]
document = check_output("pydoc-markdown -p frictionless", shell=True).decode()
target_dir = os.path.join(TARGET_DIR, "api-reference")
target_md = os.path.join(target_dir, "README.md")
os.makedirs(target_dir, exist_ok=True)
with open(target_md, "wt") as file:
    for line in document.splitlines(keepends=True):
        line = re.sub(r"^## ", "### ", line)
        line = re.sub(r"^# ", "## ", line)
        line = re.sub(r"^## frictionless$", "# API Reference", line)
        line = re.sub(r" Objects$", "", line)
        line = re.sub(r"^#### (.*)$", "#### <big>\\1</big>", line)
        file.write(line)
