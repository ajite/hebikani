import argparse
import io
import os
from unittest.mock import patch

import pytest
from colorama import Back, Fore, Style
from hebikani.typing import (
    AnswerType,
    Gender,
    HTTPMethod,
    QuestionType,
    SubjectObject,
    VoiceMode,
)
from hebikani.hebikani import (
    MAX_NB_SUJECTS,
    MIN_NB_SUBJECTS,
    Client,
    ClientOptions,
    ReviewSession,
    Subject,
    api_request,
    audio_cache,
    chunks,
    clear_audio_cache,
    clear_terminal,
    range_int_type,
    wanikani_tag_to_color,
)

from .data import (
    API_KEY,
    double_reading_subject,
    get_all_assignments,
    get_specific_subjects,
    get_subject_without_utf_entry,
    get_summary,
    vocabulary_subject,
)


@patch("requests.put")
@patch("requests.post")
@patch("requests.get")
def test_wrong_api_key(mock_requests_get, mock_requests_post, mock_requests_put):
    """Test the wrong api key."""
    mock_requests_get.return_value.status_code = 401
    mock_requests_post.return_value.status_code = 401
    mock_requests_put.return_value.status_code = 401

    with pytest.raises(ValueError):
        api_request(HTTPMethod.GET, "/summary", "wrong_api_key")

    with pytest.raises(ValueError):
        api_request(HTTPMethod.POST, "/summary", "wrong_api_key", {})

    with pytest.raises(ValueError):
        api_request(HTTPMethod.PUT, "/summary", "wrong_api_key", {})


def test_api_request_invalid_http_method():
    """Test the invalid http method."""
    with pytest.raises(ValueError):
        api_request("TEST", "/summary", API_KEY)


@patch("hebikani.hebikani.api_request", return_value=get_summary)
def test_client_summary(mock_api_request):
    """Test the summary we get from the API."""
    client = Client(API_KEY)
    summary = client.summary()
    assert summary.lessons == [25, 26]
    assert summary.reviews == [21, 23, 24]
    assert summary.nb_lessons == 2
    assert summary.nb_reviews == 3


@patch("hebikani.hebikani.api_request", return_value=get_specific_subjects)
def test_client_subject_per_ids(mock_api_request):
    """Test the retrieving subject per ids."""
    client = Client(API_KEY)
    subjects = client._subject_per_ids([440])
    assert subjects[0].id == 440
    assert subjects[0].object == SubjectObject.KANJI
    assert subjects[0].context_sentences == []
    assert subjects[0].component_subject_ids == [1]


def test_vocabulary_subject():
    subject = Subject(vocabulary_subject)
    assert subject.object == "vocabulary"
    assert subject.component_subject_ids == [440]
    assert len(subject.context_sentences) == 3
    assert subject.context_sentences[0].en == "Let’s meet up once."
    assert subject.context_sentences[0].ja == "一ど、あいましょう。"


@patch("hebikani.hebikani.api_request", return_value=get_all_assignments)
def test_client_assignment_id_per_subject_id(mock_api_request):
    """Test the retrieving assignment per subject id."""
    client = Client(API_KEY)
    assignment_id = client._assignment_id_per_subject_id(8761)
    assert assignment_id == 80463006


@patch("requests.get")
def test_ascii_art(mock_request_get):
    """Check if the ASCII art is correctly displayed."""
    """Test the ascii art creation when no utf character."""

    # 32x32 png image sample from WaniKani API
    img_f = open(os.path.join(os.path.dirname(__file__), "assets/no_utf.png"), "rb")

    # the image in ascii the desired ASCII format
    ascii_f = open(os.path.join(os.path.dirname(__file__), "assets/no_utf.txt"), "r")

    class MockClass:
        """To mock the requests.get."""

        @classmethod
        def json(cls):
            return get_subject_without_utf_entry

        content = img_f.read()
        status_code = 200

    mock_request_get.return_value = MockClass

    client = Client(API_KEY)
    subjects = client._subject_per_ids([8769])
    assert subjects[0].id == 8769

    # The card front should be the same as the ascii art
    assert subjects[0].characters == ascii_f.read()


def test_card_audio_creation():
    """Test the card creation with audio."""
    subject = Subject(vocabulary_subject)
    assert subject.object == "vocabulary"

    # Test we only have one audio since one of them is not an mp3
    assert len(subject.audios) == 2
    assert (
        subject.audios[0].url
        == "https://cdn.wanikani.com/audios/3020-subject-2467.mp3?1547862356"
    )  # noqa: E501
    assert subject.audios[0].ext == ".mp3"


@patch("builtins.input", return_value="y")
@patch("hebikani.hebikani.Audio.play")
def test_review_session_audio_mode(audio_play_mock, input_mock):
    """Test the review session audio mode."""
    subject = Subject(vocabulary_subject)
    options = ClientOptions(voice_mode=VoiceMode.FEMALE)
    client = Client(API_KEY, options)
    session = ReviewSession(client, [subject] * 10)

    # Test only with reading card type
    assert len(session.queue) == 20

    # removes all the meaning
    session.queue = list(
        filter(lambda c: c.question_type == QuestionType.READING, session.queue)
    )

    # check we have half
    assert len(session.queue) == 10

    # Test with female audio
    for card in session.queue:
        session.ask_audio(card)
        assert session.last_audio_played.voice_gender == Gender.FEMALE

    # Test with male voice
    session.client.options.voice_mode = VoiceMode.MALE

    for card in session.queue:
        session.ask_audio(card)
        assert session.last_audio_played.voice_gender == Gender.MALE

    # Test with alternate voice
    session.client.options.voice_mode = VoiceMode.ALTERNATE

    # Get the last audio gender before alternating
    current_gender = session.last_audio_played.voice_gender

    for card in session.queue:
        session.ask_audio(card)
        assert session.last_audio_played.voice_gender != current_gender
        current_gender = session.last_audio_played.voice_gender


def test_card_answer():
    """Test"""
    subject = Subject(get_specific_subjects["data"][0])
    readings = subject.readings
    meanings = subject.meanings

    assert len(readings.answers) == 3
    assert len(readings.acceptable_answers) == 1
    assert len(readings.unacceptable_answers) == 2
    assert len(meanings.answers) == 1

    assert meanings.primary.value == "one"
    assert readings.primary.value == "いち"

    assert readings.solve("いち") == AnswerType.CORRECT
    assert readings.solve("ひと") == AnswerType.INEXACT
    assert readings.solve("かず") == AnswerType.INEXACT
    assert readings.solve("ちい") == AnswerType.INCORRECT
    assert meanings.solve("ones") == AnswerType.A_BIT_OFF
    assert meanings.solve("onsen") == AnswerType.INCORRECT
    assert meanings.solve("first") == AnswerType.INCORRECT

    # Check with a longer word

    meanings.primary.data["meaning"] = "skillful"
    assert meanings.primary.value == "skillful"

    assert meanings.solve("skillful") == AnswerType.CORRECT
    assert meanings.solve("skilfull") == AnswerType.A_BIT_OFF
    assert meanings.solve("unskilfull") == AnswerType.INCORRECT


def test_card_is_solved():
    """Test the card is solved."""
    subject = Subject(vocabulary_subject)
    assert subject.solved is False

    subject.meaning_question.solve("one")
    subject.reading_question.solve("いち")

    assert subject.solved is True

    subject = Subject(vocabulary_subject)

    assert subject.solved is False

    subject.meaning_question.solve("hello")
    subject.reading_question.solve("いち")

    assert subject.solved is False


def test_hard_mode():
    """Test the hard mode."""
    subject = Subject(double_reading_subject)
    readings = subject.readings
    meanings = subject.meanings

    assert len(readings.answers) == 3
    assert len(readings.acceptable_answers) == 2
    assert len(meanings.answers) == 1

    assert meanings.solve("what") == AnswerType.CORRECT
    assert readings.solve("なに") == AnswerType.CORRECT
    assert readings.solve("なん") == AnswerType.CORRECT
    assert readings.solve("なに,なん", True) == AnswerType.CORRECT
    assert readings.solve("なん,なに", True) == AnswerType.CORRECT
    assert readings.solve("なん , なに ", True) == AnswerType.CORRECT
    assert readings.solve("なんあ , なに ", True) == AnswerType.INCORRECT
    assert readings.solve("なん , はははは ", True) == AnswerType.INEXACT
    assert readings.solve(" はははは , なに", True) == AnswerType.INEXACT
    assert readings.solve("なん , はははは , なに", True) == AnswerType.INCORRECT

    subject = Subject(get_specific_subjects["data"][0])
    readings = subject.readings
    meanings = subject.meanings

    assert len(readings.acceptable_answers) == 1
    assert readings.solve("いち", True) == AnswerType.CORRECT
    assert readings.solve("ひと", True) == AnswerType.INEXACT
    assert readings.solve("かず", True) == AnswerType.INEXACT


def test_review_session():
    """Test"""
    subject = Subject(vocabulary_subject)
    client = Client(API_KEY)
    session = ReviewSession(client, [subject] * 10)
    assert len(session.queue) == 20
    assert session.nb_subjects == 10


def test_mnemonics():
    """Test the mnemonics."""
    subject = Subject(vocabulary_subject)
    assert subject.reading_question.mnemonic == (
        "When a vocab word is all alone and has no okurigana "
        "(hiragana attached to kanji) connected to it, it usually "
        "uses the kun'yomi reading. Numbers are an exception, however. "
        "When a number is all alone, with no kanji or okurigana, it is "
        "going to be the on'yomi reading, which you learned with the kanji.  "
        "Just remember this exception for alone numbers and you'll be able to "
        "read future number-related vocab to come."
    )
    assert subject.meaning_question.mnemonic == (
        "As is the case with most vocab words that consist of a single kanji, "
        "this vocab word has the same meaning as the kanji it parallels, which "
        "is \u003cvocabulary\u003eone\u003c/vocabulary\u003e."
    )


def test_wanikani_tag_to_color():
    """Test the WaniKani tag to color."""
    text = "This is a <ja>test</ja>."
    result = (
        f"This is a {Style.BRIGHT + Fore.WHITE + Back.GREEN}test"
        f"{Back.RESET + Fore.RESET + Style.RESET_ALL}."
    )
    assert wanikani_tag_to_color(text) == result

    text = "This <kanji>is</kanji> a <radical>test</radical>."
    result = (
        f"This {Style.BRIGHT + Fore.WHITE + Back.RED}is"
        f"{Back.RESET + Fore.RESET + Style.RESET_ALL} a "
        f"{Style.BRIGHT + Fore.WHITE + Back.BLUE}test"
        f"{Back.RESET + Fore.RESET + Style.RESET_ALL}."
    )

    assert wanikani_tag_to_color(text) == result


def test_chunks():
    """It should divided array into chuncks

    E.g:
        chuncks([1, 2, 3, 4, 5, 6, 7], 2)
        returns: [[1, 2], [3, 4], [5, 6], [7]]
    """
    assert list(chunks([1, 2, 3, 4, 5, 6, 7], 2)) == [[1, 2], [3, 4], [5, 6], [7]]
    assert list(chunks([1, 2, 3, 4, 5, 6], 3)) == [[1, 2, 3], [4, 5, 6]]


@patch("os.name", "nt")
@patch("os.system")
def test_clear_terminal_windows(os_system):
    """It should clear the terminal in windows"""
    clear_terminal()
    os_system.assert_called_with("cls")


@patch("os.name", "posix")
@patch("os.system")
def test_clear_terminal_posix(os_system):
    """It should clear the terminal in linux/mac"""
    clear_terminal()
    os_system.assert_called_with("clear")


def test_argparse_range_int_type():
    """Validate the range of an int"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=range_int_type)

    # Test when the value is too low
    with pytest.raises(SystemExit):
        parser.parse_args(["--limit", str(MIN_NB_SUBJECTS - 1)])

    # Test when the value is too high
    with pytest.raises(SystemExit):
        parser.parse_args(["--limit", str(MAX_NB_SUJECTS + 1)])

    # Test when the value is correct (highest possible value)
    try:
        parser.parse_args(["--limit", str(MAX_NB_SUJECTS)])
    except SystemExit:
        pytest.fail("It should not raise SystemExit")

    # Test when the value is correct (lowest possible value)
    try:
        parser.parse_args(["--limit", str(MIN_NB_SUBJECTS)])
    except SystemExit:
        pytest.fail("It should not raise SystemExit")

    # Test with invalid value (float)
    with pytest.raises(SystemExit):
        parser.parse_args(["--limit", "1.5"])

    # Test with invalid value (string)
    with pytest.raises(SystemExit):
        parser.parse_args(["--limit", "test"])


def test_clear_audio_cache():
    """It should clear the audio cache"""
    assert len(audio_cache) == 0

    # Create some fake files. It does not need to be a mp3 file.
    f = io.BytesIO()
    f.write(b"test")
    audio_cache["test"] = f
    assert len(audio_cache) == 1

    # File should be opened
    assert f.closed is False

    clear_audio_cache()

    # File should be closed
    assert f.closed is True
