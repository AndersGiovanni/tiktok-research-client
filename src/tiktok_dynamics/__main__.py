"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """TikTok Dynamics."""


if __name__ == "__main__":
    main(prog_name="tiktok-dynamics")  # pragma: no cover
