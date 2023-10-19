"""Test cases for general utilities."""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tiktok_research_client.utils import (
    generate_date_ranges,  # Replace 'your_module' with the actual module name
)
from tiktok_research_client.utils import read_json
from tiktok_research_client.utils import save_json


class TestGeneralUtilities(unittest.TestCase):
    """Test cases for general utilities."""

    def test_read_json(self) -> None:
        """Test reading json from a file."""
        with TemporaryDirectory() as tmpdirname:
            tmp_path = Path(tmpdirname) / "test.json"
            data = [{"key": "value", "number": 1}]
            with open(tmp_path, "w") as f:
                json.dump(data, f)

            read_data = read_json(tmp_path)
            self.assertEqual(read_data, data)

    def test_save_json(self) -> None:
        """Test saving json to a file."""
        with TemporaryDirectory() as tmpdirname:
            tmp_path = Path(tmpdirname) / "test_save.json"
            data = [{"key": "value"}]
            save_json(tmp_path, data)

            with open(tmp_path) as f:
                saved_data = json.load(f)
            self.assertEqual(saved_data, data)

    def test_generate_date_ranges(self) -> None:
        """Test generating date ranges."""
        start_date_str = "2022-01-01"
        total_days = 100
        ranges = generate_date_ranges(start_date_str, total_days)

        # Perform some basic checks.
        self.assertTrue(isinstance(ranges, list))
        self.assertTrue(all(isinstance(r, tuple) for r in ranges))
        self.assertTrue(all(len(r) == 2 for r in ranges))

        # More specific assertions can be added based on your requirements.
        # For example, you might want to validate that the date ranges are
        # each 30 days apart (except maybe the last one), etc.


if __name__ == "__main__":
    unittest.main()
