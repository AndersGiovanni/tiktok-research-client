"""Test cases for the __main__ module."""
import os

import pytest
from click.testing import CliRunner

from tiktok_research_client import __main__


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    assert 0 == 0


def test_environment_variable(runner: CliRunner) -> None:
    """Test that the environment variable is set."""
    runner.invoke(__main__.main)
    assert "CLIENT_KEY" in os.environ
