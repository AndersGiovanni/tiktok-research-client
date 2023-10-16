"""Config file for the project."""

from pathlib import Path


# Defining paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = ROOT_DIR / "data"

DATA_USER_DIR = DATA_DIR / "users"

DATA_SEARCH_DIR = DATA_DIR / "search"

DATA_COMMENTS_DIR = DATA_DIR / "comments"
