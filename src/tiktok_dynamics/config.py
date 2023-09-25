"""Config file for the project."""

from pathlib import Path


# Defining paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = ROOT_DIR / "data"

DATA_USER_DIR = DATA_DIR / "user"

DATA_KEYWORD_DIR = DATA_DIR / "keyword"

DATA_COMMENTS_DIR = DATA_DIR / "comments"
