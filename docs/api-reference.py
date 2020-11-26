import re
import sys
from subprocess import check_output


content = check_output("pydoc-markdown -p frictionless", shell=True).decode()
for line in content.splitlines(keepends=True):
    line = re.sub(r"^## ", "### ", line)
    line = re.sub(r"^# ", "## ", line)
    line = re.sub(r"^## frictionless$", "# API Reference", line)
    line = re.sub(r" Objects$", "", line)
    line = re.sub(r"^#### (.*)$", "#### <big>\\1</big>", line)
    sys.stdout.write(line)
