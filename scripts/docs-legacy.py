import os
import gdown
import shutil
import subprocess
from urllib.parse import urlparse


SOURCE_DIR = os.path.join("docs", "source")
TARGET_DIR = os.path.join("docs", "target")


# Converters


def from_markdown(source, target):
    if isinstance(source, (tuple, list)):
        source = os.path.join(*source)
    target_dir = os.path.join(TARGET_DIR, target)
    target_md = os.path.join(target_dir, "README.md")
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy(source, target_md)


def from_notebook(source, target):
    target_dir = os.path.join(TARGET_DIR, target)
    target_md = os.path.join(target_dir, "README.md")
    target_py = os.path.join(target_dir, "README.ipynb")
    os.makedirs(target_dir, exist_ok=True)
    url = f"https://drive.google.com/uc?id={os.path.split(urlparse(source).path)[-1]}"
    gdown.download(url, target_py, quiet=True)
    #  command = f"python3 -m json.tool {target_py} > {target_py}_tmp"
    #  subprocess.run(command, shell=True, check=True)
    #  command = f"mv {target_py}_tmp {target_py}"
    #  subprocess.run(command, shell=True, check=True)
    command = f"python3 -m nbconvert --to markdown {target_py} --log-level 0"
    subprocess.run(command, shell=True, check=True)
    lines = []
    codeblock = []
    with open(target_md) as file:
        for index, line in enumerate(file.read().splitlines()):
            line = line.replace("[0m", "")
            line = line.replace("[1m", "")
            line = line.rstrip()
            if index == 1:
                lines.append(
                    f"\n[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)]({source})\n\n"
                )
            if line.startswith("```"):
                if not codeblock:
                    codeblock.append("```python" if line == "```" else line)
                else:
                    codeblock.append("```")
                    lines.extend(codeblock)
                    codeblock = []
                continue
            if codeblock:
                codeblock.append(line)
                if line.startswith("!"):
                    codeblock[0] = "```bash"
                continue
            if "README_files" in line:
                line = line.replace("README_files", "./README_files")
            lines.append(line)
    with open(target_md, "w") as file:
        file.write("\n".join(lines))


# Main

if __name__ == "__main__":
    for path in sorted(os.listdir("docs")):
        fullpath = os.path.join("docs", path)
        if os.path.isfile(fullpath):
            subprocess.run(f"python3 {fullpath}", shell=True, check=True)
            print(f"Executed: {fullpath}")
