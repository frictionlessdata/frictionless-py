import os
import sys
import subprocess


SOURCE_DIR = os.path.join("docs")
TARGET_DIR = os.path.join("docs", "build")


# Main


def main(name=None):
    for path in sorted(os.listdir(SOURCE_DIR)):
        filename = os.path.splitext(path)[0]
        if name and name != filename:
            continue
        fullpath = os.path.join(SOURCE_DIR, path)
        if os.path.isfile(fullpath):
            if path.endswith(".py"):
                from_python(filename)
            elif path.endswith(".md"):
                from_markdown(filename)
            print(f"Built: {filename}")


# Converters


def from_python(name):
    source_py = os.path.join(SOURCE_DIR, f"{name}.py")
    target_dir = os.path.join(TARGET_DIR, name)
    target_md = os.path.join(target_dir, "README.md")
    command = f"python3 {source_py}"
    content = subprocess.check_output(command, shell=True)
    os.makedirs(target_dir, exist_ok=True)
    with open(target_md, "wb") as file:
        file.write(content)


def from_markdown(name):
    source_md = os.path.join(SOURCE_DIR, f"{name}.md")
    target_dir = os.path.join(TARGET_DIR, name)
    target_md = os.path.join(target_dir, "README.md")
    target_py = os.path.join(target_dir, "README.ipynb")
    os.makedirs(target_dir, exist_ok=True)
    command = f"notedown {source_md} --run > {target_py} --match python"
    subprocess.run(command, shell=True, check=True)
    command = f"python3 -m nbconvert {target_py} --to markdown --log-level 0"
    subprocess.run(command, shell=True, check=True)
    lines = []
    with open(target_md) as file:
        for index, line in enumerate(file.read().splitlines()):
            line = line.replace("[0m", "")
            line = line.replace("[1m", "")
            line = line.rstrip()
            if "README_files" in line:
                line = line.replace("README_files", "./README_files")
            lines.append(line)
    with open(target_md, "w") as file:
        file.write("\n".join(lines))


# Main

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else None
    main(name=name)
