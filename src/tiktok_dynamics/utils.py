"""General utilities."""

import json
from pathlib import Path
from typing import Dict
from typing import Iterable
from typing import List
from typing import Union


def read_json(path: Path) -> List[Dict[str, Union[str, int]]]:
    """Read json from path."""
    with open(path, encoding="utf-8") as file:
        data: List[Dict[str, Union[str, int]]] = json.load(file)
    return data


def save_json(path: Path, container: Iterable) -> None:
    """Write dict to path."""
    print(f"Saving json to {path}")
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(container, outfile, ensure_ascii=False, indent=4)
