"""Command-line interface."""
import click

from tiktok_dynamics.config import DATA_KEYWORD_DIR
from tiktok_dynamics.config import DATA_USER_DIR
from tiktok_dynamics.data_collection.collect import TiktokClient
from tiktok_dynamics.utils import save_json


@click.command()
@click.version_option()
@click.option(
    "--query_option",
    "-q",
    type=click.Choice(["user", "keyword", "comments"]),
    help="What do you want to query? (user, keyword, comments)",
    default="user",
)
@click.option(
    "--query_input",
    "-i",
    help="What is the input? (username, keyword, video_id)",
    required=True,
)
@click.option("--collect_max", "-m", help="Max number of videos to collect", default=10)
def main(query_option: str, query_input: str, collect_max: int) -> None:
    """Tikok Dynamics.

    Args:
        query_option (str): What do you want to query? (user, keyword, comments)
        query_input (str): What is the input? (username, keyword, video_id)
        collect_max (int): Max number of videos to collect

    Raises:
        ValueError: Invalid query option

    Returns:
        None
    """
    client = TiktokClient()

    if query_option == "user":
        # Get user info
        user_data = client.get_user_info(query_input)
        # Save to json
        save_json(DATA_USER_DIR / f"{query_input}.json", user_data)

    elif query_option == "keyword":
        # Search keyword
        keyword_data = client.search_keyword(
            [query_input], paginate=True, collect_max=collect_max
        )
        # Save to json
        save_json(
            DATA_KEYWORD_DIR / f"{query_input.replace(' ','_')}.json", keyword_data
        )

    elif query_option == "comments":
        pass

    else:
        raise ValueError("Invalid query option")

    return


if __name__ == "__main__":
    main(prog_name="tiktok-dynamics")  # pragma: no cover
