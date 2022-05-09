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
from wanikani_cli.typing import (
    AnswerType,
    SubjectObject,
    Gender,
    QuestionType,
    VoiceMode,
)

__all__ = ["Client", "ClientOptions", "Subject", "ReviewSession"]

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


def http_post(endpoint: str, api_key: str, data: dict):
    """Make a POST request to the API.

    Args:
        endpoint (str): The endpoint to make the request to.
        api_key (str): The API key to use.
        data (dict): The data to send.
    """
    url = API_URL + endpoint
    headers = {"Authorization": f"Bearer {api_key}"}
    resp = requests.post(url, headers=headers, json=data)
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
        hard_mode: bool = False,
        dry_run: bool = False,
    ):
        """Initialize the client options.

        Args:
            autoplay (bool): Whether to autoplay audio.
            silent (bool): Whether to silence the output.
            voice_mode (VoiceMode): The voice mode to use.
            hard_mode (bool): Whether to use hard mode.
            dry_run (bool): Whether to run in dry run mode.
        """
        self.autoplay = autoplay
        self.silent = silent
        self.voice_mode = voice_mode
        self.hard_mode = hard_mode
        self.dry_run = dry_run


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
        session = ReviewSession(self, subjects)
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
        # We do not need to worry since meaning questions do not use
        # this attribute. It is better to use GET in case.
        return self.data.get("type", "")


class AnswerManager:
    """The answer manager."""

    def __init__(self, answers: List[Answer]):
        """Initialize the answer manager.

        Args:
            answers (List[Answer]): The answers to use.
        """
        self.answers = answers

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

    def solve(self, inputed_answer: str, hard_mode: bool = False) -> bool:
        """Check wether an answer is correct."""
        inputed_answer = inputed_answer.lower().strip()
        answer_type = AnswerType.INCORRECT
        if hard_mode and QuestionType.READING:
            # In hard mode check that all the answers are correct.
            # Only works for reading questions.
            answer_type = AnswerType.CORRECT
            if set([i.strip() for i in inputed_answer.split(",")]) == set(
                [a.value for a in self.acceptable_answers]
            ):
                answer_type = AnswerType.CORRECT
            else:
                answer_type = AnswerType.INCORRECT
        elif inputed_answer in [a.value for a in self.acceptable_answers]:
            answer_type = AnswerType.CORRECT
        # Check for close matches only when asking for the meaning
        # of a word.
        elif self.question_type == QuestionType.MEANING and get_close_matches(
            inputed_answer,
            [a.value for a in self.acceptable_answers],
            cutoff=RATIO_CLOSE_MATCHES,
        ):
            answer_type = AnswerType.A_BIT_OFF
        elif inputed_answer in [a.value for a in self.unacceptable_answers]:
            answer_type = AnswerType.INEXACT

        return answer_type


class ReviewUpdate:
    """Reviews log all the correct and incorrect answers provided through the
    'Reviews' section of WaniKani. Review records are created when a user answers
    all the parts of a subject correctly once; some subjects have both meaning
    or reading parts, and some only have one or the other.
    Note that reviews are not created for the quizzes in lessons.."""

    def __init__(
        self,
        client: Client,
        subject_id: int,
        incorrect_meaning_answers: int,
        incorrect_reading_answers: int,
    ):
        """Initialize the review update.

        Args:
            subject_id (int): The subject id.
            incorrect_meaning_answers (int): The number of incorrect meaning answers.
            incorrect_reading_answers (int): The number of incorrect reading answers.
        """
        self.client = client
        self.subject_id = subject_id
        self.incorrect_meaning_answers = incorrect_meaning_answers
        self.incorrect_reading_answers = incorrect_reading_answers

    def save(self):
        """Save the review update on WaniKani."""
        data = {
            "review": {
                "subject_id": self.subject_id,
                "incorrect_meaning_answers": self.incorrect_meaning_answers,
                "incorrect_reading_answers": self.incorrect_reading_answers,
            }
        }
        if self.client.options.dry_run is False:
            http_post("reviews", self.client.api_key, data)


class Subject(APIObject):
    """A subject."""

    def __str__(self) -> str:
        return self.object.__str__()

    def __init__(self, data):
        super().__init__(data)
        self._readings = None
        self._meanings = None
        self._meaning_question = Question(self, QuestionType.MEANING)
        self._reading_question = None
        if self.object != SubjectObject.RADICAL:
            self._reading_question = Question(self, QuestionType.READING)

    @property
    def id(self):
        """Get the subject ID."""
        return self.data["id"]

    @property
    def object(self):
        """Get the object type."""
        return self.data["object"]

    @property
    def audios(self) -> List[Audio]:
        """Get the audios for vocabulary items (only mp3).

        Returns:
            List[Audio]: The audios.
        """
        _audios = []
        if self.object == SubjectObject.VOCABULARY:
            _audios = list(
                filter(
                    lambda audio: audio.ext == ".mp3",
                    [Audio(data) for data in self.data["data"]["pronunciation_audios"]],
                )
            )
        return _audios

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

    @property
    def readings(self):
        """Get the reading of the kanji."""
        if self._readings is None:
            self._readings = AnswerManager(
                [
                    Answer(answer, QuestionType.READING)
                    for answer in self.data["data"]["readings"]
                ]
            )
        return self._readings

    @property
    def meanings(self):
        """Get the meaning of the kanji."""
        if self._meanings is None:
            self._meanings = AnswerManager(
                [
                    Answer(answer, QuestionType.MEANING)
                    for answer in self.data["data"]["meanings"]
                ]
            )
        return self._meanings

    @property
    def reading_question(self):
        """Get the reading question."""
        return self._reading_question

    @property
    def meaning_question(self):
        """Get the meaning question."""
        return self._meaning_question

    @property
    def questions(self):
        """Get the questions."""
        _questions = [self.meaning_question]
        if self.reading_question:
            _questions.append(self.reading_question)
        return _questions

    @property
    def solved(self):
        """Check if the subject is solved."""
        return all(q.solved for q in self.questions)


class Question:
    """The question."""

    def __init__(self, subject: Subject, question_type: QuestionType):
        self.subject = subject
        self.question_type = question_type
        self.wrong_answer_count = 0
        self.solved = False

    def solve(self, inputed_answer: str, hard_mode: bool = False) -> AnswerType:
        """Check wether an answer is correct.

        Args:
            inputed_answer (str): The inputed answer.


        Returns:
            AnswerType: The answer type.
        """

        _answer = None
        if self.question_type == QuestionType.READING:
            _answer = self.subject.readings.solve(inputed_answer, hard_mode)
        else:
            _answer = self.subject.meanings.solve(inputed_answer)

        if _answer == AnswerType.INCORRECT:
            self.wrong_answer_count += 1
        elif _answer == AnswerType.CORRECT:
            self.solved = True

        return _answer

    def add_wrong_answer(self):
        """Add a wrong answer.
        Used when a user tags his answer as wrong.
        """
        self.wrong_answer_count += 1

    @property
    def answer_values(self):
        """Get the answer values."""
        values = None
        if self.question_type == QuestionType.MEANING:
            values = self.subject.meanings.answer_values
        else:
            values = self.subject.readings.answer_values

        return values

    @property
    def primary(self):
        """Get the primary answer."""
        _primary = None
        if self.question_type == QuestionType.MEANING:
            _primary = self.subject.meanings.primary
        else:
            _primary = self.subject.readings.primary

        return _primary


class ReviewSession:
    """A review session."""

    def __init__(self, client: Client, subjects: List[Subject]):
        """Initialize the review session.

        Args:
            subjects (List[Subject]): The subjects.
            client (Client): The client.
        """
        self.client = client
        self.subjects = subjects
        self.queue = []
        self.nb_subjects = 0
        self.build_queue(subjects)
        self.last_audio_played = None

    def build_queue(self, subjects: List[Subject]):
        """Build the queue.

        Args:
            subjects (List[Subject]): A list of subjects.
        """
        for subject in subjects:
            self.queue.extend(subject.questions)
            self.nb_subjects += 1
        self.shuffle()

    def shuffle(self):
        """Shuffle."""
        random.shuffle(self.queue)

    def start(self):
        """Start the reviews.

        We will start with the first question in the queue.
        If the user answers correctly, we will remove the question from the deck
        and move on to the next question.
        Otherwise we will show the user the correct answer, shuffle the deck
        and move on to the next card.
        """

        nb_correct_answers = 0
        nb_incorrect_answers = 0  # Multiple error count multiple times.
        nb_completed_subjects = 0

        """Start the review session."""
        while self.queue:
            question = self.queue[0]
            clear_terminal()

            total_answers = nb_incorrect_answers + nb_correct_answers
            correct_rate = ""
            if total_answers > 0:
                correct_rate = (
                    str(round(nb_correct_answers * 100 / total_answers, 2)) + "%"
                )
            print(
                f"Review {nb_completed_subjects}/{self.nb_subjects}",
                f"- {correct_rate}:\n\n",
            )
            print(question.subject.characters)
            answer_type = None

            """We use a loop in case the user answers is not wrong but not acceptable

            E.g: the question asks for the kunyomi but we wrote the onyomi.
            We do not want to fail the user because of this. It is not a mistake.
            """
            while answer_type is None or answer_type == AnswerType.INEXACT:
                answer_type = self.ask_answer(question)
                # If the user answers correctly, we remove the card from the deck
                if answer_type == AnswerType.CORRECT:
                    print("Correct!")
                    nb_correct_answers += 1
                    del self.queue[0]
                # If the user is a bit off, we show the correct answer and ask
                # to validate his answer
                elif answer_type == AnswerType.A_BIT_OFF:
                    print(
                        "Your answer is a bit off.",
                        f"The correct answer is: {question.answer_values}",
                    )
                    if input("Do you want to validate your answer? (Y/n) ") in [
                        "n",
                        "N",
                    ]:
                        nb_incorrect_answers += 1
                        question.add_wrong_answer()
                        self.shuffle()
                    else:
                        nb_correct_answers += 1
                        question.solved = True
                        del self.queue[0]

                # If the user answers another reading, we ask the user to correct it
                elif answer_type == AnswerType.INEXACT:
                    print(
                        "Try again. We are looking for the",
                        f"{question.primary.type}.",
                    )
                # If the user answers incorrectly, we show the correct answer
                else:
                    nb_incorrect_answers += 1
                    print(
                        "Wrong ! The correct answer is:",
                        question.answer_values,
                    )
                    self.shuffle()

            subject = question.subject
            if subject.solved:
                self.nb_subjects -= 1
                nb_completed_subjects += 1
                ReviewUpdate(
                    self.client,
                    subject.id,
                    subject.meaning_question.wrong_answer_count,
                    subject.reading_question.wrong_answer_count
                    if subject.reading_question
                    else 0,
                ).save()

            self.ask_audio(question)
            input("Press a key to continue...")

        print("All done!")

    def ask_answer(self, question: Question):
        """Ask the user for an answer.

        Args:
            question (Question): The question.

        Returns:
            AnswerType: The answer type.
        """
        prompt = f"{question.subject.object} - {question.question_type}: "

        if question.question_type == QuestionType.MEANING:
            inputed_answer = input(prompt)
        else:
            inputed_answer = input_kana(prompt)

        answer_type = question.solve(inputed_answer, self.client.options.hard_mode)
        return answer_type

    def ask_audio(self, question: Question):
        """Ask the user if they want to hear the audio.

        Args:
            card (Card): The card.
        """
        if (
            self.client.options.silent
            or not question.subject.audios
            or question.question_type == QuestionType.MEANING
        ):
            return

        if self.client.options.autoplay or input(
            "Would you like to hear the audio? [y/N] "
        ) in ["y", "Y"]:
            audio = self.select_audio(question.subject.audios)
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
        if self.client.options.voice_mode == VoiceMode.FEMALE or (
            self.client.options.voice_mode == VoiceMode.ALTERNATE
            and self.last_audio_played
            and self.last_audio_played.voice_gender == Gender.MALE
        ):
            audio = list(filter(lambda a: a.voice_gender == Gender.FEMALE, audios))[0]
        elif self.client.options.voice_mode == VoiceMode.MALE or (
            self.client.options.voice_mode == VoiceMode.ALTERNATE
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

    text = "Do not play or prompt for audio. Disables autoplay. (default: False)"

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

    text = (
        "You will need to input all the correcting meanings to",
        "validate an answer. E.g: 'なん, なん' for 何. The order does not matter.",
    )

    text = (
        "Ask for all the readings separated with a comma."
        "E.g: The answer for 何　should be 'なん,なに'."
        "The order does not matter. (default: False)"
    )

    parser.add_argument("--hard", action="store_true", default=False, help=text)

    text = (
        "Do not submit answers to the WaniKani API."
        "This mode is meant for testing purposes."
    )

    parser.add_argument("--dry-run", action="store_true", default=False, help=text)
    # Extract the arguments from the parser.
    args = parser.parse_args()

    # Make sure that we've got an API key and that a mode has been set.
    if args.api_key is None:
        parser.error("api_key is required.")

    client_options = ClientOptions(
        autoplay=args.autoplay,
        silent=args.silent,
        voice_mode=args.voice,
        hard_mode=args.hard,
        dry_run=args.dry_run,
    )

    client = Client(args.api_key, options=client_options)

    res = getattr(client, args.mode)()
    # Do not display command that do not return a response.
    # They already have been displayed.
    if res:
        print(res)


if __name__ == "__main__":
    main()
