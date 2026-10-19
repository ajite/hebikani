"""Session flows driven with mocked user input."""
from unittest.mock import patch

import pytest
import requests

from hebikani.hebikani import (
    AssignmentUpdate,
    Cache,
    Client,
    ClientOptions,
    LessonSession,
    ReviewSession,
    Subject,
    api_request,
    audio_cache,
)
from hebikani.typing import AnswerType, Gender, HTTPMethod, VoiceMode

from .data import (
    API_KEY,
    double_reading_subject,
    get_all_assignments,
    get_specific_subjects,
    post_review,
    vocabulary_subject,
)

KANJI_ONE = get_specific_subjects["data"][0]


@pytest.fixture
def no_shuffle():
    """Keep the queue order deterministic."""
    with patch("hebikani.hebikani.random.shuffle"):
        yield


@patch("hebikani.hebikani.clear_terminal")
@patch("hebikani.hebikani.api_request", return_value=post_review)
@patch("hebikani.hebikani.input_kana", side_effect=["ひと", "いち"])
@patch("builtins.input", side_effect=["", "wrong", "", "", "one", ""])
def test_review_session_start(mock_input, mock_kana, mock_api, mock_clear, no_shuffle):
    """A full review: wrong meaning, inexact then correct reading, submission."""
    subject = Subject(KANJI_ONE)
    options = ClientOptions(display_mnemonics=True)
    session = ReviewSession(Client(API_KEY, options), [subject])
    session.start()

    assert subject.solved
    assert session.nb_completed_subjects == 1
    assert session.nb_subjects == 1
    assert session.nb_correct_answers == 2
    assert session.nb_incorrect_answers == 1
    assert session.correct_rate == "66.67%"
    assert subject.meaning_question.wrong_answer_count == 1
    assert subject.reading_question.wrong_answer_count == 0
    mock_api.assert_called_once_with(
        HTTPMethod.POST,
        "reviews",
        API_KEY,
        {
            "review": {
                "subject_id": 440,
                "incorrect_meaning_answers": 1,
                "incorrect_reading_answers": 0,
            }
        },
    )


def test_correct_rate_without_answers():
    session = ReviewSession(Client(API_KEY), [])
    assert session.correct_rate == "X"


@patch("hebikani.hebikani.api_request")
def test_process_subject_dry_run(mock_api):
    """Dry run never submits and keeps counting completed subjects."""
    subject = Subject(KANJI_ONE)
    session = ReviewSession(Client(API_KEY, ClientOptions(dry_run=True)), [subject])

    session.process_subject(subject)
    assert session.nb_completed_subjects == 0

    subject.meaning_question.solved = True
    subject.reading_question.solved = True
    session.process_subject(subject)
    assert session.nb_completed_subjects == 1
    mock_api.assert_not_called()


@patch("hebikani.hebikani.api_request", side_effect=[get_all_assignments, {}])
def test_process_subject_from_lesson(mock_api):
    """Lessons start the assignment instead of posting a review."""
    subject = Subject(KANJI_ONE)
    for question in subject.questions:
        question.solved = True
    session = ReviewSession(Client(API_KEY), [subject], from_lesson=True)
    session.process_subject(subject)

    assert mock_api.call_count == 2
    assert mock_api.call_args_list[1].args[:2] == (
        HTTPMethod.PUT,
        "assignments/80463006/start",
    )


@patch("hebikani.hebikani.api_request", return_value={"data": []})
def test_assignment_update_without_assignment(mock_api):
    with pytest.raises(ValueError):
        AssignmentUpdate(Client(API_KEY), 440)


@patch("hebikani.hebikani.input_kana", return_value="なに,なん")
def test_ask_answer_hard_mode_prompt(mock_kana):
    """Hard mode tells how many readings are expected."""
    subject = Subject(double_reading_subject)
    session = ReviewSession(Client(API_KEY, ClientOptions(hard_mode=True)), [subject])
    assert session.ask_answer(subject.reading_question) == AnswerType.CORRECT
    mock_kana.assert_called_once_with("kanji - reading (2 answers): ")


@patch("builtins.input", side_effect=["", "one"])
def test_ask_answer_rejects_empty_meaning(mock_input):
    subject = Subject(KANJI_ONE)
    session = ReviewSession(Client(API_KEY), [subject])
    assert session.ask_answer(subject.meaning_question) == AnswerType.CORRECT
    assert mock_input.call_count == 2


@patch("hebikani.hebikani.handler", side_effect=SystemExit)
@patch("hebikani.hebikani.input_kana", side_effect=KeyboardInterrupt)
def test_ask_answer_interrupt(mock_kana, mock_handler):
    subject = Subject(KANJI_ONE)
    session = ReviewSession(Client(API_KEY), [subject])
    with pytest.raises(SystemExit):
        session.ask_answer(subject.reading_question)
    mock_handler.assert_called_once()


@patch("builtins.input", return_value="n")
def test_process_answer_a_bit_off_refused(mock_input):
    subject = Subject(KANJI_ONE)
    session = ReviewSession(Client(API_KEY), [subject])
    session.process_answer(subject.meaning_question, AnswerType.A_BIT_OFF)
    assert subject.meaning_question.wrong_answer_count == 1
    assert session.queue == [subject.meaning_question]

    mock_input.return_value = "y"
    session.process_answer(subject.meaning_question, AnswerType.A_BIT_OFF)
    assert subject.meaning_question.solved


@patch("builtins.input", return_value="n")
def test_ask_audio_declined(mock_input):
    subject = Subject(vocabulary_subject)
    session = ReviewSession(Client(API_KEY), [subject])
    session.ask_audio(subject.reading_question)
    assert session.last_audio_played is None

    session.client.options.silent = True
    session.ask_audio(subject.reading_question)
    assert mock_input.call_count == 1


@patch("hebikani.hebikani.Audio.play")
def test_select_audio_random_and_cached(mock_play):
    audios = Subject(vocabulary_subject).audios
    session = ReviewSession(
        Client(API_KEY, ClientOptions(voice_mode=VoiceMode.RANDOM)), []
    )
    assert session.select_audio(audios) in audios

    # Alternate mode without history has no preference either.
    session.client.options.voice_mode = VoiceMode.ALTERNATE
    assert session.select_audio(audios) in audios

    # A cached audio always wins over the preferred gender.
    male = [a for a in audios if a.voice_gender == Gender.MALE][0]
    audio_cache[male.url] = None
    session.client.options.voice_mode = VoiceMode.FEMALE
    assert session.select_audio(audios) is male


@patch("hebikani.hebikani.threading.Thread")
@patch("hebikani.hebikani.Audio.download")
def test_audio_play(mock_download, mock_thread):
    audio = Subject(vocabulary_subject).audios[0]
    audio_cache[audio.url] = type("File", (), {"name": "audio.mp3"})
    audio.play()
    mock_download.assert_called_once()
    mock_thread.assert_called_once()
    assert mock_thread.call_args.kwargs["args"] == ("audio.mp3",)
    mock_thread.return_value.start.assert_called_once()
    audio_cache.clear()


@patch("hebikani.hebikani.requests.get")
def test_audio_download_http_error(mock_get):
    mock_get.return_value.raise_for_status.side_effect = requests.HTTPError
    audio = Subject(vocabulary_subject).audios[0]
    with pytest.raises(requests.HTTPError):
        audio.download()
    assert audio_cache == {}


@patch("requests.get")
def test_api_request_not_modified_and_errors(mock_get):
    """304 returns None with the If-Modified-Since header, other errors raise."""
    import datetime

    mock_get.return_value.status_code = 304
    since = datetime.datetime(
        2018, 4, 11, 8, tzinfo=datetime.timezone(datetime.timedelta(hours=8))
    )
    assert (
        api_request(HTTPMethod.GET, "subjects", API_KEY, modified_since=since) is None
    )
    headers = mock_get.call_args.kwargs["headers"]
    assert headers["If-Modified-Since"] == "Wed, 11 Apr 2018 00:00:00 GMT"
    assert headers["Authorization"] == f"Bearer {API_KEY}"

    mock_get.return_value.status_code = 500
    mock_get.return_value.raise_for_status.side_effect = requests.HTTPError
    with pytest.raises(requests.HTTPError):
        api_request(HTTPMethod.GET, "subjects", API_KEY)


@patch("hebikani.hebikani.clear_terminal")
@patch("hebikani.hebikani.Audio.download")
@patch("hebikani.hebikani.Audio.play")
@patch("hebikani.hebikani.Client._subject_per_ids", return_value=[Subject(KANJI_ONE)])
@patch(
    "hebikani.hebikani.getch",
    side_effect=[b"x", b"\x1b", b"[", b"D", b"C", b"\n", b"K", b"\r", b"M", b"M"],
)
def test_lesson_interface_navigation(
    mock_getch, mock_ids, mock_play, mock_download, mock_clear
):
    """Arrows and enter move through the tabs, leaving after the last one."""
    subject = Subject(vocabulary_subject)
    session = LessonSession(Client(API_KEY), [subject])
    session.lesson_interface(subject)

    # ignored keys, left (stays on the first tab), right, enter, left, enter,
    # right, right (past the last tab)
    assert mock_getch.call_count == 10
    mock_download.assert_called_once()
    mock_play.assert_called()


@patch("hebikani.hebikani.getch", side_effect=[b"\n"])
def test_lesson_interface_silent(mock_getch):
    """Radicals have a single tab and no audio is fetched in silent mode."""
    subject = Subject(KANJI_ONE)
    subject.data["object"] = "radical"
    session = LessonSession(Client(API_KEY, ClientOptions(silent=True)), [subject])
    with patch("hebikani.hebikani.clear_terminal"):
        session.lesson_interface(subject)
    assert mock_getch.call_count == 1


@patch("hebikani.hebikani.ReviewSession.start")
@patch("hebikani.hebikani.LessonSession.lesson_interface")
@patch("hebikani.hebikani.clear_terminal")
@patch("builtins.input", return_value="")
def test_lesson_session_start(mock_input, mock_clear, mock_interface, mock_review):
    """Subjects are shown by batch, each batch followed by a quiz."""
    subjects = [Subject(KANJI_ONE) for _ in range(4)]
    LessonSession(Client(API_KEY), subjects).start()
    assert mock_interface.call_count == 4
    assert mock_review.call_count == 2
    # start, continue between the two batches
    assert mock_input.call_count == 2


@patch("hebikani.hebikani.ReviewSession.start")
@patch("hebikani.hebikani.Client.summary")
@patch("hebikani.hebikani.load_settings", return_value=[KANJI_ONE])
def test_client_reviews_uses_cache_and_summary(mock_load, mock_summary, mock_start):
    mock_summary.return_value.reviews = [440]
    Client(API_KEY).reviews()
    assert Cache.subjects[440].id == 440
    mock_start.assert_called_once()


@patch("hebikani.hebikani.LessonSession.start")
@patch("hebikani.hebikani.Client.summary")
@patch("hebikani.hebikani.Client._subject_per_ids", return_value=[])
@patch("hebikani.hebikani.load_settings", return_value={})
def test_client_lessons_with_test_ids(mock_load, mock_ids, mock_summary, mock_start):
    Client(API_KEY, ClientOptions(test_ids=[1, 2])).lessons()
    mock_summary.assert_not_called()
    mock_ids.assert_called_once_with([1, 2])
    mock_start.assert_called_once()
