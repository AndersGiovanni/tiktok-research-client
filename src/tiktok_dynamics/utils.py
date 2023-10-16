"""General utilities."""

import json
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Union


def read_json(path: Path) -> List[Dict[str, Union[str, int]]]:
    """Read json from path."""
    with open(path, encoding="utf-8") as file:
        data: List[Dict[str, Union[str, int]]] = json.load(file)
    return data


def save_json(path: Path, container: Iterable[Dict[str, Any]]) -> None:
    """Write dict to path."""
    print(f"Saving json to {path}")
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(container, outfile, ensure_ascii=False, indent=4)


def generate_date_ranges(start_date_str: str, total_days: int) -> List[tuple[str, str]]:
    """Generate data ranges.

    Parameters
    ----------
    start_date_str : _type_
        Start date in string format.
    total_days : _type_
        How many days to generate.

    Returns
    -------
    List[tuple[str, str]]
        Date ranges.
    """
    date_format = "%Y-%m-%d"
    start_date = datetime.strptime(start_date_str, date_format)
    end_date = start_date + timedelta(days=total_days)

    date_ranges = []

    while start_date < end_date:
        next_date = start_date + timedelta(days=30)

        if next_date > end_date:
            next_date = end_date

        date_ranges.append(
            (
                start_date.strftime(date_format).replace("-", ""),
                next_date.strftime(date_format).replace("-", ""),
            )
        )

        start_date = next_date + timedelta(days=1)

    return date_ranges

if __name__ == "__main__":

    pass

    a = generate_date_ranges("2021-01-01", 100)
    b = 1
