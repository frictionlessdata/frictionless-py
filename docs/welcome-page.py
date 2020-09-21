import os
import shutil
from scripts import docs


shutil.copy("README.md", os.path.join(docs.TARGET_DIR, "README.md"))
