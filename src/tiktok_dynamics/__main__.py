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
    default="keyword",
)
@click.option(
    "--query_input",
    "-i",
    help="What is the input? (username, keyword, video_id)",
    required=True,
)
@click.option("--collect_max", "-m", help="Max number of videos to collect", default=10)
@click.option(
    "--start_date",
    "-d",
    help="What should the start date be? Default: 2022-01-01",
    default="2022-01-01",
)
@click.option(
    "--total_days",
    "-td",
    help="How big of a window should we look for? Collect max has higher priority. Default: 100 days",
    default=100,
)
@click.option(
    "--region_code",
    "-r",
    help="Which regions/countries? Separate by ','. Select 'ALL' for all countries. Default: US",
    default="US",
)
@click.option(
    "--collect_comments",
    "-cc",
    help="Do you want to collect comments for the videos? Default: False",
    default=True,
)
def main(
    query_option: str,
    query_input: str,
    collect_max: int,
    start_date: str,
    total_days: int,
    region_code: str,
    collect_comments: bool,
) -> None:
    """Tikok Dynamics.

    Args:
        query_option (str): What do you want to query? (user, keyword, comments)
        query_input (str): What is the input? (username, keyword, video_id)
        collect_max (int): Max number of videos to collect
        start_date (str): What should the start date be? Default: 2022-01-01
        total_days (int): How big of a window should we look for? Collect max has higher priority. Default: 100 days
        region_code (str): Which regions/countries? Separate by ','. Select 'ALL' for all countries. Default: US

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
            [query_input],
            paginate=True,
            collect_max=collect_max,
            start_date=start_date,
            total_days=total_days,
            region_code=region_code,
            collect_comments=collect_comments,
        )
        # Save to json
        if len(keyword_data) == 0:
            print("No data collected. Please try again.")
        else:
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
