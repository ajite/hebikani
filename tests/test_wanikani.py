import os
from unittest.mock import patch

from wanikani_cli.typing import AnswerType, QuestionType, Gender, VoiceMode
from wanikani_cli.wanikani import Client, ClientOptions, Kanji, ReviewSession, Subject

from .data import (
    API_KEY,
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
    assert subjects[0].object_type == "kanji"
    assert isinstance(subjects[0].object, Kanji)


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
    assert subjects[0].object.cards[0].front == ascii_f.read()


def test_card_audio_creation():
    """Test the card creation with audio."""
    subject = Subject(vocabulary_subject)
    assert subject.object_type == "vocabulary"

    # Test we only have one audio since one of them is not an mp3
    assert len(subject.object.audios) == 2
    assert (
        subject.object.audios[0].url
        == "https://cdn.wanikani.com/audios/3020-subject-2467.mp3?1547862356"
    )  # noqa: E501
    card_meaning, card_reading = subject.object.cards
    assert card_meaning.question_type == QuestionType.MEANING
    assert card_reading.question_type == QuestionType.READING

    assert card_meaning.audios is None
    assert len(card_reading.audios) == 2
    assert (
        card_reading.audios[0].url
        == "https://cdn.wanikani.com/audios/3020-subject-2467.mp3?1547862356"
    )  # noqa: E501
    assert card_reading.audios[0].ext == ".mp3"


@patch("wanikani_cli.wanikani.Audio.play")
@patch("builtins.input", return_value="y")
def test_review_session_audio_mode(audio_play_mock, input):
    """Test the review session audio mode."""
    subject = Subject(vocabulary_subject)
    options = ClientOptions(voice_mode=VoiceMode.FEMALE)
    session = ReviewSession([subject] * 10, options=options)

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
    session.options.voice_mode = VoiceMode.MALE

    for card in session.queue:
        session.ask_audio(card)
        assert session.last_audio_played.voice_gender == Gender.MALE

    # Test with alternate voice
    session.options.voice_mode = VoiceMode.ALTERNATE

    # Get the last audio gender before alternating
    current_gender = session.last_audio_played.voice_gender

    for card in session.queue:
        session.ask_audio(card)
        assert session.last_audio_played.voice_gender != current_gender
        current_gender = session.last_audio_played.voice_gender


def test_card_answer():
    """Test"""
    subject = Subject(get_specific_subjects["data"][0])
    meaning, reading = subject.object.cards

    assert len(reading.answer_manager.answers) == 3
    assert len(reading.answer_manager.acceptable_answers) == 1
    assert len(reading.answer_manager.unacceptable_answers) == 2
    assert len(meaning.answer_manager.answers) == 1

    assert meaning.answer_manager.primary.value == "one"
    assert reading.answer_manager.primary.value == "いち"

    assert reading.solve("いち") == AnswerType.CORRECT
    assert reading.solve("ひと") == AnswerType.INEXACT
    assert reading.solve("かず") == AnswerType.INEXACT
    assert reading.solve("ちい") == AnswerType.INCORRECT
    assert meaning.solve("ones") == AnswerType.A_BIT_OFF
    assert meaning.solve("onsen") == AnswerType.INCORRECT
    assert meaning.solve("first") == AnswerType.INCORRECT

    # Check with a longer word

    meaning.answer_manager.primary.data["meaning"] = "skillful"
    assert meaning.answer_manager.primary.value == "skillful"

    assert meaning.solve("skillful") == AnswerType.CORRECT
    assert meaning.solve("skilfull") == AnswerType.A_BIT_OFF
    assert meaning.solve("unskilfull") == AnswerType.INCORRECT


def test_review_session_acceptable_answer():
    """Test"""
    subject = Subject(vocabulary_subject)
    meaning, reading = subject.object.cards

    # assert card.solve("いち") is True
    # assert card.solve("ひと") is True
