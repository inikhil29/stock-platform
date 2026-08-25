"""
Unit tests for Core utility functions.
"""

import gzip
from pathlib import Path
from unittest.mock import patch

from core.utilities.file_utilities import extract_gzip_file
from core.utilities.printing_utilities import clear_line


class TestFileUtilities:
    """Test suite for file compression and decompression utilities."""

    def test_extract_gzip_file(self, tmp_path: Path):
        content = b"instrument_key,tradingsymbol\nNSE_EQ|INE002A01018,RELIANCE"
        gz_path = tmp_path / "instruments.json.gz"
        out_path = tmp_path / "instruments.json"

        # Create temporary gzip archive
        with gzip.open(gz_path, "wb") as f_out:
            f_out.write(content)

        # Decompress
        result_path = extract_gzip_file(str(gz_path), str(out_path))

        assert result_path == str(out_path)
        assert out_path.exists()
        assert out_path.read_bytes() == content


class TestPrintingUtilities:
    """Test suite for console output utilities."""

    @patch("sys.stdout.write")
    @patch("sys.stdout.flush")
    def test_clear_line(self, mock_flush, mock_write):
        clear_line()
        assert mock_write.call_count == 2
        mock_flush.assert_called_once()

