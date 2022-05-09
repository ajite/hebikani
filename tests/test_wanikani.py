import os
from unittest.mock import patch

from wanikani_cli.typing import (
    AnswerType,
    Gender,
    QuestionType,
    SubjectObject,
    VoiceMode,
)
from wanikani_cli.wanikani import Client, ClientOptions, ReviewSession, Subject

from .data import (
    API_KEY,
    double_reading_subject,
    get_specific_subjects,
    get_subject_without_utf_entry,
    get_summary,
    vocabulary_subject,
)


@patch("wanikani_cli.wanikani.http_get")
def test_summary(mock_http_get):
    """Test the summary."""
    mock_http_get.return_value = get_summary
    client = Client(API_KEY)
    summary = client.summary()
    assert summary.lessons == [25, 26]
    assert summary.reviews == [21, 23, 24]
    assert summary.nb_lessons == 2
    assert summary.nb_reviews == 3


@patch("wanikani_cli.wanikani.http_get")
def test_subjects_creation(mock_http_get):
    """Test the subjects creation."""
    mock_http_get.return_value = get_specific_subjects
    client = Client(API_KEY)
    subjects = client._subject_per_id([440])
    assert subjects[0].id == 440
    assert subjects[0].object == SubjectObject.KANJI


@patch("requests.get")
def test_ascii_art(mock_request_get):
    """Check if the ASCII art is correctly displayed."""
    """Test the ascii art creation when no utf character."""

    # 32x32 png image sample from wanikani API
    img_f = open(os.path.join(os.path.dirname(__file__), "assets/no_utf.png"), "rb")

    # the image in ascii the desired ASCII format
    ascii_f = open(os.path.join(os.path.dirname(__file__), "assets/no_utf.txt"), "r")

    class MockClass:
        """To mock the requests.get."""

        @classmethod
        def json(cls):
            return get_subject_without_utf_entry

        content = img_f.read()

    mock_request_get.return_value = MockClass

    client = Client(API_KEY)
    subjects = client._subject_per_id([8769])
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


@patch("wanikani_cli.wanikani.Audio.play")
@patch("builtins.input", return_value="y")
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


def test_hard_mode():
    """Test the hard mode."""
    subject = Subject(double_reading_subject)
    readings = subject.readings
    meanings = subject.meanings

    assert len(readings.answers) == 2
    assert len(readings.acceptable_answers) == 2
    assert len(meanings.answers) == 1

    assert meanings.solve("what") == AnswerType.CORRECT
    assert readings.solve("なに") == AnswerType.CORRECT
    assert readings.solve("なん") == AnswerType.CORRECT
    assert readings.solve("なに,なん", True) == AnswerType.CORRECT
    assert readings.solve("なん,なに", True) == AnswerType.CORRECT
    assert readings.solve("なん , なに ", True) == AnswerType.CORRECT
    assert readings.solve("なんあ , なに ", True) == AnswerType.INCORRECT


def test_review_session():
    """Test"""
    subject = Subject(vocabulary_subject)
    client = Client(API_KEY)
    session = ReviewSession(client, [subject] * 10)
    assert len(session.queue) == 20
    assert session.nb_subjects == 10
