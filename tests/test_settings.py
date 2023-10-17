import os
from unittest.mock import patch
import hebikani.settings as settings


@patch("sys.platform", "darwin")
def test_get_settings_path_darwin():
    """Test getting the settings path."""
    assert settings.get_settings_path("hebikani") == os.path.expanduser(
        "~/Library/Application Support/hebikani"
    )


@patch("sys.platform", "linux")
def test_get_settings_path_linux():
    """Test getting the settings path."""
    assert settings.get_settings_path("hebikani") == os.path.expanduser(
        "~/.config/hebikani"
    )


@patch("sys.platform", "win32")
def test_get_settings_path_win32():
    """Test getting the settings path."""
    assert settings.get_settings_path("hebikani") == os.path.expanduser("~/hebikani")


@patch("sys.platform", "cygwin")
def test_get_settings_path_cygwin():
    """Test getting the settings path."""
    assert settings.get_settings_path("hebikani") == os.path.expanduser("~/hebikani")


def test_save_settings():
    """Test saving settings."""
    settings.save_settings("test.json", {"test": "test"})
    assert os.path.exists(
        os.path.join(settings.get_settings_path("hebikani"), "test.json")
    )
    os.remove(os.path.join(settings.get_settings_path("hebikani"), "test.json"))
    assert not os.path.exists(
        os.path.join(settings.get_settings_path("hebikani"), "test.json")
    )


def test_load_settings():
    """Test loading settings."""
    settings.save_settings("test.json", {"test": "test"})
    assert settings.load_settings("test.json") == {"test": "test"}
    os.remove(os.path.join(settings.get_settings_path("hebikani"), "test.json"))
    assert settings.load_settings("test.json") == {}
    assert not os.path.exists(
        os.path.join(settings.get_settings_path("hebikani"), "test.json")
    )
