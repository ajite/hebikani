"""Define all the enums used in the CLI."""


class HTTPMethod:
    """Define the HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"


class AnswerType:
    """Enum for the answer type."""

    CORRECT = "correct"
    INCORRECT = "incorrect"
    INEXACT = "inexact"  # right answer to another question (e.g. onyomi vs kunyomi)
    A_BIT_OFF = "a_bit_off"  # close to a correct meaning (typo)


class QuestionType:
    """Define the question types."""

    MEANING = "meaning"
    READING = "reading"


class SubjectObject:
    """Subject objects."""

    RADICAL = "radical"
    KANJI = "kanji"
    VOCABULARY = "vocabulary"
    KANA_VOCABULARY = "kana_vocabulary"


class Gender:
    """Gender"""

    FEMALE = "female"
    MALE = "male"


class VoiceMode:
    """Voice Mode"""

    ALTERNATE = "alternate"
    RANDOM = "random"
    FEMALE = "female"
    MALE = "male"
