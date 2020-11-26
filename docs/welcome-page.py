import os

TARGET_DIR = os.environ["TARGET_DIR"]
os.system(f"cp README.md {TARGET_DIR}/README.md")
