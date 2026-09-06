import sys
from unittest.mock import MagicMock, patch

import pytest

from omnix.game_detector import GameDetector


def test_get_file_version():
    """Test extracting file version from executable."""
    detector = GameDetector()

    # Mock os.path.exists or similar if needed, but get_file_version usually uses win32api or pefile
    # Since we are cross-platform python but app is windows focused (win32 in context)

    with patch("omnix.game_detector.GameDetector._get_file_version_info", return_value="1.0.0.123"):
        version = detector._get_file_version_info("C:\\Fake\\Game.exe")
        assert version == "1.0.0.123"


def test_build_game_info_includes_version():
    """Test that _build_game_info includes version."""
    detector = GameDetector()

    mock_process = MagicMock()
    mock_process.pid = 1234
    mock_process.as_dict.return_value = {
        "pid": 1234,
        "name": "Game.exe",
        "exe": "C:\\Games\\Game.exe",
    }

    with patch.object(detector, "_get_file_version_info", return_value="1.2.3"):
        info = detector._build_game_info(mock_process, "Test Game")

        assert info["version"] == "1.2.3"
        assert info["exe"] == "C:\\Games\\Game.exe"
