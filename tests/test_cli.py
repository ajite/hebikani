from unittest.mock import patch

import pytest

from hebikani.hebikani import build_parser, handler, main
from hebikani.typing import VoiceMode


def test_parser_defaults(monkeypatch):
    monkeypatch.setenv("WANIKANI_API_KEY", "ENV_KEY")
    args = build_parser().parse_args(["summary"])
    assert args.api_key == "ENV_KEY"
    assert args.limit == 50
    assert args.voice == VoiceMode.ALTERNATE
    assert not args.dry_run

    with pytest.raises(SystemExit):
        build_parser().parse_args(["unknown"])


@patch("hebikani.hebikani.Client.summary", return_value="A summary")
@patch("builtins.print")
def test_main_prints_result(mock_print, mock_summary):
    with patch("sys.argv", ["hebikani", "summary", "-k", "KEY"]):
        main()
    mock_print.assert_called_with("A summary")


@patch("hebikani.hebikani.Client.summary", side_effect=ValueError("Invalid API Key"))
@patch("builtins.print")
def test_main_prints_errors(mock_print, mock_summary):
    with patch("sys.argv", ["hebikani", "summary", "-k", "KEY"]):
        main()
    mock_print.assert_called_with(mock_summary.side_effect)


@patch("hebikani.hebikani.Client.reviews")
def test_main_test_ids_imply_dry_run(mock_reviews):
    argv = ["hebikani", "reviews", "-k", "KEY", "--test-ids", "41,50", "--hard"]
    with patch("sys.argv", argv), patch(
        "hebikani.hebikani.Client.__init__", return_value=None
    ) as init:
        main()
    options = init.call_args.kwargs["options"]
    assert options.dry_run
    assert options.hard_mode
    assert options.test_ids == [41, 50]


def test_main_requires_api_key(monkeypatch):
    monkeypatch.delenv("WANIKANI_API_KEY", raising=False)
    with patch("sys.argv", ["hebikani", "summary"]), pytest.raises(SystemExit):
        main()


@patch("hebikani.hebikani.clear_terminal")
@patch("hebikani.hebikani.clear_audio_cache")
def test_handler_exits(mock_clear_cache, mock_clear):
    with pytest.raises(SystemExit):
        handler()
    mock_clear_cache.assert_called_once()
