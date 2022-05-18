"""Define all the enums used in the CLI."""


class HTTPMethod(object):
    """Define the HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"


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


class SubjectObject(enumerate):
    """Subject objects."""

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
