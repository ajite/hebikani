#!/usr/bin/env python
import os
import random
import tempfile
from argparse import ArgumentParser, RawTextHelpFormatter
from difflib import get_close_matches
from io import BytesIO
from typing import List

import ascii_magic
import requests
from PIL import Image, ImageOps
from playsound import playsound

from wanikani_cli import __version__
from wanikani_cli.input import input_kana
from wanikani_cli.typing import AnswerType, CardType, Gender, QuestionType, VoiceMode

__all__ = ["Client", "ClientOptions", "Kanji", "Subject", "ReviewSession"]

API_URL = "https://api.wanikani.com/v2/"

# Ratio when using difflib.get_close_matches()
RATIO_CLOSE_MATCHES = 0.8


def http_get(endpoint: str, api_key: str):
    """Make a GET request to the API.

    Args:
        endpoint (str): The endpoint to make the request to.
        api_key (str): The API key to use.
    """
    url = API_URL + endpoint
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = requests.get(url, headers=headers)
    return resp.json()


def url_to_ascii(url: str):
    """Uses ascii_magic to generate an ascii art image from an image downloaded
    from a URL.
    Args:
        url (str): The url of the image we want to convert to ascii art.
    """
    request = requests.get(url)
    downloaded_image_file = BytesIO(request.content)
    downloaded_image = Image.open(downloaded_image_file)

    # Downloaded image mode is LA.
    # Create a white rgba background
    image = Image.new("RGBA", downloaded_image.size, "white")
    image.paste(downloaded_image, (0, 0), downloaded_image)
    image = ImageOps.invert(image.convert("RGB"))

    ascii_art = ascii_magic.from_image(image, columns=64)
    return ascii_art


def clear_terminal():
    """Clear the terminal."""
    os.system("cls" if os.name == "nt" else "clear")


class ClientOptions:
    """Client options."""

    def __init__(
        self,
        autoplay: bool = False,
        silent: bool = False,
        voice_mode: VoiceMode = VoiceMode.ALTERNATE,
    ):
        """Initialize the client options.

        Args:
            autoplay (bool): Whether to autoplay audio.
            silent (bool): Whether to silence the output.
            voice_mode (VoiceMode): The voice mode to use.
        """
        self.autoplay = autoplay
        self.silent = silent
        self.voice_mode = voice_mode


class Client:
    """The main client class.

    Usage:
        >>> import wanikani
        >>> client = wanikani.Client('API_KEY')
    """

    def __init__(self, api_key: str, options: ClientOptions = None):
        """Initialize the client.

        Args:
            api_key (str): The API key to use.
            options (ClientOptions): The client options .
        """
        self.api_key = api_key
        self.options = options or ClientOptions()

    def summary(self):
        """Get a summary of the user's current progress."""
        data = http_get("summary", self.api_key)
        return Summary(data)

    def reviews(self):
        """Get reviews for a subject.

        Args:
            subject_id (int): The subject ID to get reviews for.
        """
        subjects = self._subject_per_id(self.summary().reviews)
        session = ReviewSession(subjects, options=self.options)
        session.start()

    def lessons(self):
        """Get lessons from the wanikani server. Not currently implemented."""
        raise NotImplementedError()

    def _subject_per_id(self, subject_ids: List[int]):
        """Get subjects by ID.

        Args:
            subject_ids (List[int]): A list of subject IDs to get.
        """
        ids = ",".join(str(i) for i in subject_ids)
        data = http_get(f"subjects?ids={ids}", self.api_key)
        return [Subject(subject) for subject in data["data"]]


class APIObject:
    """Base class for API objects."""

    def __init__(self, data):
        """Initialize the lesson.

        Args:
            data (dict): The data to use.
        """
        self.data = data


class Audio(APIObject):
    """Audio object."""

    @property
    def url(self):
        """Get the audio url."""
        return self.data["url"]

    @property
    def ext(self):
        """Get the audio file extension."""
        _ext = ".ogg"
        if self.data["content_type"] == "audio/mpeg":
            _ext = ".mp3"
        return _ext

    @property
    def voice_gender(self) -> Gender:
        """The gender of the voice actor."""
        _gender = Gender.FEMALE
        if self.data["metadata"]["gender"] == Gender.MALE:
            _gender = Gender.MALE

        return _gender

    def play(self):
        """Download and play the audio."""
        r = requests.get(self.url)
        f = tempfile.NamedTemporaryFile(suffix=self.ext)
        f.write(r.content)
        f.seek(0)
        playsound(f.name)
        f.close()


class Summary(APIObject):
    """The summary of the user's current progress."""

    def __str__(self) -> str:
        return f"""Summary:
    Lessons: {self.nb_lessons}
    Reviews: {self.nb_reviews}"""

    @property
    def lessons(self):
        """Get the lessons available."""
        return self.data["data"]["lessons"][0]["subject_ids"]

    @property
    def reviews(self):
        """Get the reviews available."""
        return self.data["data"]["reviews"][0]["subject_ids"]

    @property
    def nb_lessons(self):
        """Get the number of lessons available."""
        return len(self.lessons)

    @property
    def nb_reviews(self):
        """Get the number of reviews available."""
        return len(self.reviews)


class Answer(APIObject):
    """The answer to a review."""

    def __init__(self, data, question_type: QuestionType):
        """Initialize the answer.

        Args:
            data (dict): The data to use.
            question_type (QuestionType): The question type.
        """
        super().__init__(data)
        self.question_type = question_type

    @property
    def is_primary(self) -> bool:
        """Whether the answer is the primary answer.

        Returns:
            bool: Whether the answer is the primary answer.
        """
        return self.data["primary"]

    @property
    def is_acceptable(self) -> bool:
        """Whether the answer is acceptable.

        Returns:
            bool: Whether the answer is acceptable.
        """
        return self.data["accepted_answer"]

    @property
    def value(self) -> str:
        """Get the value of the answer."""
        return self.data[self.question_type].lower().strip()

    @property
    def type(self) -> str:
        """Get the type of the answer (onyomi, kunyomi, nanori)."""

        # We do not need to worry since meaning do not have this attribute
        # Still It is better to use GET in case.
        return self.data.get("type", "")


class AnswerManager:
    """The answer manager."""

    def __init__(self, answers: List[Answer]):
        """Initialize the answer manager.

        Args:
            answers (List[Answer]): The answers to use.
        """
        self.answers = answers

    def add(self, answer: Answer):
        """Add an answer.

        Args:
            answer (Answer): The answer to add.
        """
        self.answers.append(answer)

    @property
    def primary(self) -> Answer:
        """Get the primary answer.

        Returns:
            Answer: The primary answer.

        Raises:
            ValueError: If no primary answer is found.
        """
        answers = list(filter(lambda a: a.is_primary, self.answers))
        if len(answers) == 0:
            raise ValueError("No primary answer found.")
        return answers[0]

    @property
    def acceptable_answers(self) -> List[Answer]:
        """Get the acceptable answers.

        Returns:
            List[Answer]: The acceptable answers.
        """
        return list(filter(lambda a: a.is_acceptable, self.answers))

    @property
    def unacceptable_answers(self) -> List[Answer]:
        """Get the unacceptable answers.

        Returns:
            List[Answer]: The unacceptable answers.
        """
        return list(filter(lambda a: not a.is_acceptable, self.answers))

    @property
    def question_type(self) -> QuestionType:
        """Get the question type.

        Returns:
            QuestionType: The question type.
        """
        return self.primary.question_type

    @property
    def answer_values(self) -> str:
        """Get the answer values in a string.

        Returns:
            str: The answer values join with a comma.
        """
        return ", ".join(a.value for a in self.acceptable_answers)


class Card:
    """A card."""

    def __init__(
        self,
        front: str,
        answer_manager: AnswerManager,
        card_type: CardType,
        audios: List[Audio] = None,
    ):
        """Initialize the card.

        Args:
            front (str): The front of the card.
            answer_manager (AnswerManager): The answer manager.
            card_type (CardType): The type of card.
            audios (List[Audio]): The audios.
        """
        self.front = front
        self.answer_manager = answer_manager
        self.card_type = card_type
        self.audios = audios

    @property
    def question_type(self) -> QuestionType:
        """Get the question type.

        Returns:
            QuestionType: The question type.
        """
        return self.answer_manager.question_type

    def solve(self, inputed_answer: str):
        """Check wether an answer is correct."""
        inputed_answer = inputed_answer.lower().strip()
        answer_type = AnswerType.INCORRECT
        if inputed_answer in [a.value for a in self.answer_manager.acceptable_answers]:
            answer_type = AnswerType.CORRECT
        # Check for close matches only when asking for the meaning
        # of a word.
        elif (
            self.answer_manager.question_type == QuestionType.MEANING
            and get_close_matches(
                inputed_answer,
                [a.value for a in self.answer_manager.acceptable_answers],
                cutoff=RATIO_CLOSE_MATCHES,
            )
        ):
            answer_type = AnswerType.A_BIT_OFF
        elif inputed_answer in [
            a.value for a in self.answer_manager.unacceptable_answers
        ]:
            answer_type = AnswerType.INEXACT

        return answer_type


class Radical(APIObject):
    """A radical."""

    def __str__(self):
        return f"Radical: {self.characters}"

    @property
    def type(self):
        """Get the type."""
        return CardType.RADICAL

    @property
    def characters(self):
        """Get the characters of the radical or its ascii image."""
        _characters = self.data["data"]["characters"]
        if not _characters:
            _characters = self.ascii
        return _characters

    @property
    def ascii(self):
        """Get the ascii art of the radical from its image.

        Returns:
            str: The ascii art or None if we can't find the URL.
        """
        url = None
        _ascii = None

        # Get the image URL. We want the smallest png.
        for image in self.data["data"]["character_images"]:
            content_type = image.get("content_type")
            dimensions = image.get("metadata", {}).get("dimensions")
            if content_type == "image/png" and dimensions == "32x32":
                url = image.get("url")
                break

        if url:
            _ascii = url_to_ascii(url)

        return _ascii

    def answer_manager(self, question_type: QuestionType) -> AnswerManager:
        """Build and get the answer manager.

        Args:
            question_type (QuestionType): The question type.

        Returns:
            AnswerManager: The answer manager.
        """
        return AnswerManager(
            [
                Answer(answer, question_type)
                for answer in self.data["data"][question_type + "s"]
            ]
        )

    @property
    def cards(self):
        """Get the card."""
        return [
            Card(
                self.characters,
                self.answer_manager(QuestionType.MEANING),
                self.type,
            )
        ]


class Kanji(Radical):
    """A Kanji."""

    def __str__(self) -> str:
        return f"""Vocabulary: {self.characters}
        Readings: {self.readings}
        Meanings: {self.meanings}"""

    @property
    def type(self):
        """Get the type."""
        return CardType.KANJI

    @property
    def characters(self):
        """Get the characters of the kanji."""
        return self.data["data"]["characters"]

    @property
    def cards(self):
        """Get the cards.
        Kanji and Vocabulary cards have meaning and reading.
        """
        _cards = super(Kanji, self).cards
        _cards.append(
            Card(self.characters, self.answer_manager(QuestionType.READING), self.type)
        )
        return _cards


class Vocabulary(Kanji):
    """A vocabulary"""

    @property
    def type(self):
        """Get the type."""
        return CardType.VOCABULARY

    @property
    def audios(self):
        """Get the audios of the vocabulary (only mp3)."""
        return list(
            filter(
                lambda audio: audio.ext == ".mp3",
                [Audio(data) for data in self.data["data"]["pronunciation_audios"]],
            )
        )

    @property
    def cards(self):
        """Get the cards.
        Kanji and Vocabulary cards have meaning and reading.
        """
        _cards = super(Vocabulary, self).cards
        _cards[-1].audios = self.audios
        return _cards


class Subject(APIObject):
    """A subject."""

    def __str__(self) -> str:
        return self.object.__str__()

    @property
    def id(self):
        """Get the subject ID."""
        return self.data["id"]

    @property
    def object_type(self):
        """Get the object type."""
        return self.data["object"]

    @property
    def object(self):
        """Get the object type.

        Returns:
            APIObject: Instance of the APIObject.
        """
        _object = None
        if self.object_type == "radical":
            _object = Radical(self.data)
        elif self.object_type == "kanji":
            _object = Kanji(self.data)
        else:
            _object = Vocabulary(self.data)
        return _object


class ReviewSession:
    """A review session."""

    def __init__(self, subjects: List[Subject], options: ClientOptions = None):
        """Initialize the review session.

        Args:
            subjects (List[Subject]): The subjects.
            options (ClientOptions): The options.
        """
        self.queue = []
        self.build_queue(subjects)
        self.options = options
        self.last_audio_played = None

    def build_queue(self, subjects: List[Subject]):
        """Build the queue.

        Args:
            subjects (List[Subject]): A list of subjects.
        """
        for subject in subjects:
            self.queue.extend(subject.object.cards)
        self.shuffle()

    def shuffle(self):
        """Shuffle."""
        random.shuffle(self.queue)

    def start(self):
        """Start the reviews.

        We will start with the first card in the queue.
        If the user answers correctly, we will remove the card from the deck
        and move on to the next card.
        Otherwise we will show the user the correct answer, shuffle the deck
        and move on to the next card.
        """

        nb_correct_answers = 0
        nb_incorrect_answers = 0

        """Start the review session."""
        while self.queue:
            card = self.queue[0]
            clear_terminal()

            total_answers = nb_incorrect_answers + nb_correct_answers
            correct_rate = ""
            if total_answers > 0:
                correct_rate = (
                    str(round(nb_correct_answers * 100 / total_answers, 2)) + "%"
                )
            print(
                f"Review {nb_correct_answers}/{len(self.queue)} - {correct_rate}:\n\n"
            )  # noqa: E501
            print(card.front)
            answer_type = None

            """We use a loop in case the user answers is not wrong but not acceptable

            E.g: the question asks for the kunyomi but we wrote the onyomi.
            We do not want to fail the user because of this. It is not a mistake.
            """
            while answer_type is None or answer_type == AnswerType.INEXACT:
                answer_type = self.ask_answer(card)

                # If the user answers correctly, we remove the card from the deck
                if answer_type in AnswerType.CORRECT:
                    print("Correct!")
                    nb_correct_answers += 1
                    del self.queue[0]
                # If the user is a bit off, we show the correct answer and ask
                # to validate his answer
                elif answer_type == AnswerType.A_BIT_OFF:
                    print(
                        "Your answer is a bit off.",
                        f"The correct answer is: {card.answer_manager.answer_values}",
                    )
                    if input("Do you want to validate your answer? (Y/n) ") in [
                        "n",
                        "N",
                    ]:
                        nb_incorrect_answers += 1
                        self.shuffle()
                    else:
                        nb_correct_answers += 1
                        del self.queue[0]

                # If the user answers another reading, we ask the user to correct it
                elif answer_type == AnswerType.INEXACT:
                    print(
                        "Try again. We are looking for the",
                        f"{card.answer_manager.primary.type}.",
                    )
                # If the user answers incorrectly, we show the correct answer
                else:
                    nb_incorrect_answers += 1
                    print(
                        "Wrong ! The correct answer is:",
                        card.answer_manager.answer_values,
                    )
                    self.shuffle()

            self.ask_audio(card)
            input("Press a key to continue...")

        print("All done!")

    def ask_answer(self, card: Card):
        """Ask the user for an answer.

        Args:
            card (Card): The card.

        Returns:
            AnswerType: The answer type.
        """
        if card.question_type == QuestionType.MEANING:
            inputed_answer = input(f"{card.card_type} - {card.question_type}: ")
        else:
            inputed_answer = input_kana(f"{card.card_type} - {card.question_type}: ")

        answer_type = card.solve(inputed_answer)
        return answer_type

    def ask_audio(self, card: Card):
        """Ask the user if they want to hear the audio.

        Args:
            card (Card): The card.
        """
        if self.options.silent or not card.audios:
            return

        if self.options.autoplay or input(
            "Would you like to hear the audio? [y/N] "
        ) in ["y", "Y"]:
            audio = self.select_audio(card.audios)
            audio.play()
            self.last_audio_played = audio

    def select_audio(self, audios: List[Audio]) -> Audio:
        """Select the audio to play.

        Args:
            audios (List[Audio]): The audios.

        Returns:
            Audio: The audio to play.
        """
        audio = None

        #  In alternate mode select a random voice actor to begin with
        #  We then alternate with female and male voice actors
        if self.options.voice_mode == VoiceMode.FEMALE or (
            self.options.voice_mode == VoiceMode.ALTERNATE
            and self.last_audio_played
            and self.last_audio_played.voice_gender == Gender.MALE
        ):
            audio = list(filter(lambda a: a.voice_gender == Gender.FEMALE, audios))[0]
        elif self.options.voice_mode == VoiceMode.MALE or (
            self.options.voice_mode == VoiceMode.ALTERNATE
            and self.last_audio_played
            and self.last_audio_played.voice_gender == Gender.FEMALE
        ):
            audio = list(filter(lambda a: a.voice_gender == Gender.MALE, audios))[0]
        else:
            random_index = random.randrange(len(audios))
            audio = audios[random_index]

        return audio


def main():
    """Run the client."""
    # Work out what commands have been implemented.
    commands = [x for x in dir(Client) if not x.startswith("_")]
    # Make a version of commands that is nice to print.
    command_str = str(commands)[::-1].replace(",", " or"[::-1], 1)[-2:0:-1]

    cli_description = "A Python client for the Wanikani API."
    # Note that usage is automatically generated.
    parser = ArgumentParser(
        description=cli_description, formatter_class=RawTextHelpFormatter
    )

    text = "The mode in which wanikani-cli will run. Must be " + command_str

    parser.add_argument("mode", choices=commands, help=text)

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    text = (
        "The API key to use. Defaults to the WANIKANI_API_KEY environment " "variable."
    )

    parser.add_argument(
        "-k", "--api-key", default=os.environ.get("WANIKANI_API_KEY"), help=text
    )

    text = (
        "Auto play audio when available. Does not work with --silent."
        "(default: False)"
    )

    parser.add_argument("--autoplay", action="store_true", default=False, help=text)

    text = "Do not play or prompt for audio. Disables autoplay." "(default: False)"

    parser.add_argument("-s", "--silent", action="store_true", default=False, help=text)

    parser.add_argument(
        "--voice",
        choices=[
            VoiceMode.ALTERNATE,
            VoiceMode.RANDOM,
            VoiceMode.FEMALE,
            VoiceMode.MALE,
        ],
        default=VoiceMode.ALTERNATE,
        help=f"""{VoiceMode.ALTERNATE}: alternates between female and male voice actors
{VoiceMode.RANDOM}: plays a ramdom voice actor.
{VoiceMode.FEMALE}: plays a female voice actress.
{VoiceMode.MALE}: plays a male voice actor.
(default: {VoiceMode.ALTERNATE})""",
    )

    # Extract the arguments from the parser.
    args = parser.parse_args()

    # Make sure that we've got an API key and that a mode has been set.
    if args.api_key is None:
        parser.error("api_key is required.")

    client_options = ClientOptions(
        autoplay=args.autoplay, silent=args.silent, voice_mode=args.voice
    )

    client = Client(args.api_key, options=client_options)

    res = getattr(client, args.mode)()
    # Do not display command that do not return a response.
    # They already have been displayed.
    if res:
        print(res)


if __name__ == "__main__":
    main()
