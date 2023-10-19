"""Command-line interface."""
import logging
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Union

import click
from dotenv import load_dotenv
from halo import Halo  # type: ignore

from tiktok_research_client.data_collection.collect import TiktokClient
from tiktok_research_client.utils import save_json


@click.command()
@click.version_option()
@click.option(
    "--query_option",
    "-q",
    type=click.Choice(["user", "search", "comments"]),
    help="What do you want to query? (user, search, comments)",
    default="keyword",
)
@click.option(
    "--query_input",
    "-i",
    help="What is the input? (username, search, video_id). For keywords, separate by ','.",
    required=True,
)
@click.option(
    "--collect_max",
    "-m",
    help="Max number of videos to collect (Default: 100)",
    default=100,
)
@click.option(
    "--start_date",
    "-d",
    help="What should the start date be? Default: 2023-01-01",
    default="2023-01-01",
)
def main(
    query_option: str,
    query_input: str,
    collect_max: int,
    start_date: str,
) -> None:
    """Tikok Dynamics.

    Args:
        query_option (str): What do you want to query? (user, keyword, comments)
        query_input (str): What is the input? (username, keyword, video_id)
        collect_max (int): Max number of videos to collect
        start_date (str): What should the start date be? Default: 2022-01-01

    Raises:
        ValueError: Invalid query option
    """
    client = TiktokClient()

    load_dotenv()

    logging.info("Starting data collection...")
    logging.debug(f"Query option: {query_option}")
    logging.debug(f"Query input: {query_input}")
    logging.debug(f"Collect max: {collect_max}")
    logging.debug(f"Start date: {start_date}")

    spinner = Halo(text="Collecting data...", spinner="moon")
    spinner.start()

    if query_option == "user":
        # Get user info
        user_data: Union[Dict[str, Any], None] = client.get_user(query_input)
        # Save to json
        save_json(Path(".data/users") / f"{query_input}.json", user_data)

    elif query_option == "search":
        # Search keyword
        search_data = client.search(
            query_input.split(","),
            start_date=start_date,
            max_size=collect_max,
        )
        # Save to json
        if len(search_data) == 0:
            print("No data collected. Please try again.")
        else:
            save_json(
                Path(".data/search") / f"{query_input.replace(' ','_')}.json",
                search_data,
            )

    elif query_option == "comments":
        # Get comments
        comments_data = client.get_comments(query_input)

        if len(comments_data) == 0:
            print("No data collected. Please try again.")
        else:
            save_json(Path(".data/comments") / f"{query_input}.json", comments_data)

    else:
        raise ValueError("Invalid query option")

    spinner.stop()


if __name__ == "__main__":
    main(prog_name="tiktok-research-client")  # pragma: no cover
