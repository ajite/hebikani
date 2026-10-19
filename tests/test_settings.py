import datetime
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


@patch("sys.platform", "linux")
def test_get_settings_path_linux_xdg(monkeypatch, tmp_path):
    """Test XDG_CONFIG_HOME takes precedence on linux."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert settings.get_settings_path("hebikani") == str(tmp_path / "hebikani")


@patch("sys.platform", "win32")
def test_get_settings_path_win32(monkeypatch):
    """Test getting the settings path."""
    monkeypatch.delenv("APPDATA", raising=False)
    assert settings.get_settings_path("hebikani") == os.path.expanduser("~/hebikani")


@patch("sys.platform", "win32")
def test_get_settings_path_win32_appdata(monkeypatch, tmp_path):
    """Test APPDATA takes precedence on windows."""
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert settings.get_settings_path("hebikani") == str(tmp_path / "hebikani")


@patch("sys.platform", "cygwin")
def test_get_settings_path_cygwin(monkeypatch):
    """Test getting the settings path."""
    monkeypatch.delenv("APPDATA", raising=False)
    assert settings.get_settings_path("hebikani") == os.path.expanduser("~/hebikani")


@patch("sys.platform", "freebsd")
def test_get_settings_path_other():
    """Test getting the settings path on an unknown platform."""
    assert settings.get_settings_path("hebikani") == os.path.expanduser("~/.hebikani")


def test_save_and_load_settings(settings_dir):
    """Test saving creates the directory and loading reads it back."""
    assert not settings_dir.exists()
    settings.save_settings("test.json", {"test": "test"})
    assert (settings_dir / "test.json").exists()
    assert settings.load_settings("test.json") == {"test": "test"}

    os.remove(settings_dir / "test.json")
    assert settings.load_settings("test.json") == {}


def test_setting_modified_date(settings_dir):
    """Test the modification date is None until the file exists."""
    assert settings.setting_modified_date("test.json") is None
    settings.save_settings("test.json", {})
    modified = settings.setting_modified_date("test.json")
    assert isinstance(modified, datetime.datetime)
    assert abs((datetime.datetime.now() - modified).total_seconds()) < 5
