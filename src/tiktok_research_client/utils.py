"""General utilities."""

import json
import logging
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Tuple
from typing import Union


def read_json(path: Path) -> List[Dict[str, Union[str, int]]]:
    """Read json from path."""
    with open(path, encoding="utf-8") as file:
        data: List[Dict[str, Union[str, int]]] = json.load(file)
    return data


def save_json(
    path: Path, container: Union[Iterable[Dict[str, Any]], Dict[str, Any], None]
) -> None:
    """Write dict to path."""
    print(f"Saving json to {path}")

    # Ensure the directory exists; mkdir(parents=True) will create any missing parent directories
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(container, outfile, ensure_ascii=False, indent=4)


def generate_date_ranges(start_date_str: str, total_days: int) -> List[Tuple[str, str]]:
    """Generate date ranges for TikTok API.

    Args:
        start_date_str (str): Start date in string format.
        total_days (int): Total number of days to collect.

    Returns:
        List[str]: List of date ranges.
    """
    date_format = "%Y-%m-%d"
    start_date = datetime.strptime(start_date_str, date_format)
    end_date = start_date + timedelta(days=total_days)

    # If the end date is in the future, set it to today
    if end_date > datetime.now():
        end_date = datetime.now()

    logging.debug(
        "Generating date ranges from %s to %s (%s days), with 30 days per range (max allowed by TikTok API)",  # noqa
        start_date,
        end_date,
        total_days,
    )

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
