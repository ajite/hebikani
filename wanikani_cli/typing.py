"""Define all the enums used in the CLI."""


class AnswerType(enumerate):
    """Enum for the answer type."""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    INEXACT = "inexact"  # when the answer is not correct but is close
    A_BIT_OFF = "a_bit_off"  # when the answer is not correct but is close


class QuestionType(enumerate):
    """Define the question types."""

    MEANING = "meaning"
    READING = "reading"


class CardType(enumerate):
    """Card types."""

    RADICAL = "radical"
    KANJI = "kanji"
    VOCABULARY = "vocabulary"


class Gender(enumerate):
    """Gender"""

    FEMALE = "female"
    MALE = "male"


class VoiceMode(enumerate):
    """Voice Mode"""

    ALTERNATE = "alternate"
    RANDOM = "random"
    FEMALE = "female"
    MALE = "male"
