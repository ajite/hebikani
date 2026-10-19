import pytest

from hebikani.hebikani import Cache, audio_cache


@pytest.fixture(autouse=True)
def reset_global_state():
    """Keep the module level caches from leaking between tests."""
    Cache.subjects = {}
    Cache.client = None
    audio_cache.clear()
    yield
    Cache.subjects = {}
    Cache.client = None
    audio_cache.clear()


@pytest.fixture
def settings_dir(tmp_path, monkeypatch):
    """Store settings under a temporary directory instead of the user's home."""
    monkeypatch.setattr(
        "hebikani.settings.get_settings_path", lambda name: str(tmp_path / name)
    )
    return tmp_path / "hebikani"
