#!/usr/bin/env python
"""CLI for the WaniKani API.

Usage:
    >>> hebikani --help

    or in python

    >>> from hebikani import hebikani
    >>> client = hebikani.Client(API_KEY)
"""
import datetime
import os
import random
import re
import sys
import tempfile
import threading
import time
from argparse import ArgumentParser, ArgumentTypeError, RawTextHelpFormatter
from difflib import get_close_matches
from io import BytesIO
from platform import system
from signal import SIGINT, signal
from typing import Iterator, List

import ascii_magic
import requests
import romkan
from cairosvg import svg2png
from colorama import Back, Fore, Style
from PIL import Image, ImageOps
from playsound import playsound

from hebikani import __version__
from hebikani.graph import hist
from hebikani.input import getch, input_kana
from hebikani.typing import (
    AnswerType,
    Gender,
    HTTPMethod,
    QuestionType,
    SubjectObject,
    VoiceMode,
)
from hebikani.settings import load_settings, save_settings, setting_modified_date
from halo import Halo

if system() == "Windows":
    from mutagen.mp3 import MP3

API_URL = "https://api.wanikani.com/v2/"

# Timeout in seconds for HTTP requests (API, audio and image downloads).
REQUEST_TIMEOUT = 30

MIN_NB_SUBJECTS = 1
MAX_NB_SUJECTS = 500

# Number of subjects inside a session queue at once.
MAX_QUEUE_SIZE = 10

# Number of subjects shown before each lesson quiz.
LESSON_BATCH_SIZE = 3

# Ratio when using difflib.get_close_matches()
RATIO_CLOSE_MATCHES = 0.8

# Key codes accepted by the lesson interface (unix and windows variants).
KEYS_ENTER = (10, 13)
KEYS_RIGHT = (67, 77)
KEYS_LEFT = (68, 75)

# Cache audio during session to avoid redownloading the same audio
audio_cache = {}


def api_request(
    method: HTTPMethod, endpoint: str, api_key: str, json=None, modified_since=None
) -> dict:
    """Make an API request with correct headers.

    Args:
        method (HTTPMethod): The HTTP method to use.
        endpoint (str): The endpoint to make the request to.
        api_key (str): The API key to use.
        json (dict): The data to send.
        modified_since (datetime.datetime):
            The date to use for the If-Modified-Since header.

    Returns:
        dict: The response from the API.

    Raises:
        ValueError: If the method is not a valid HTTP method.
    """
    url = endpoint if API_URL in endpoint else API_URL + endpoint
    headers = {"Authorization": f"Bearer {api_key}"}

    if modified_since:
        headers["If-Modified-Since"] = modified_since.astimezone(
            datetime.timezone.utc
        ).strftime("%a, %d %b %Y %H:%M:%S GMT")
    if method == HTTPMethod.GET:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    elif method in (HTTPMethod.POST, HTTPMethod.PUT):
        resp = getattr(requests, method.lower())(
            url, headers=headers, json=json or {}, timeout=REQUEST_TIMEOUT
        )
    else:
        raise ValueError("Invalid HTTP method")
    if resp.status_code == 401:
        raise ValueError("Invalid API Key")
    if resp.status_code == 304:
        return None
    resp.raise_for_status()
    return resp.json()


def url_to_ascii(url: str):
    """Uses ascii_magic to generate an ascii art image from an image downloaded
    from a URL.
    Args:
        url (str): The url of the image we want to convert to ascii art.
    """
    request = requests.get(url, timeout=REQUEST_TIMEOUT)
    request.raise_for_status()

    # Convert svg to png
    downloaded_image_file = BytesIO()

    # CairoSVG did not like the #000 color in the svg
    content = (
        request.content.decode("utf-8").replace("#000", "rgb(0,0,0)").encode("utf-8")
    )

    svg2png(bytestring=content, write_to=downloaded_image_file)

    downloaded_image = Image.open(downloaded_image_file)

    # Downloaded image mode is LA.
    # Create a white rgba background
    image = Image.new("RGBA", downloaded_image.size, "white")
    image.paste(downloaded_image, (0, 0), downloaded_image)
    image = ImageOps.invert(image.convert("RGB"))

    return ascii_magic.from_image(image, columns=64)


def wanikani_tag_to_color(text: str) -> str:
    """Convert a WaniKani tag to a color.

    Args:
        text (str): The text to convert.

    Returns:
        str: The colorized text.
    """
    tag_colors = {
        "kanji": Back.RED,
        "vocabulary": Back.MAGENTA,
        "radical": Back.BLUE,
        "ja": Back.GREEN,
        "reading": Back.CYAN,
        "meaning": Back.CYAN,
    }
    for tag, bg_color in tag_colors.items():
        text = text.replace(f"<{tag}>", Style.BRIGHT + Fore.WHITE + bg_color)
        text = text.replace(f"</{tag}>", Back.RESET + Fore.RESET + Style.RESET_ALL)
    return text


def clear_terminal():
    """Clear the terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def clear_audio_cache():
    """Delete the cached audio files."""
    for audio_file in audio_cache.values():
        os.unlink(audio_file.name)
    audio_cache.clear()


def handler(signal_received=None, frame=None):
    """Terminate the program gracefully."""
    clear_terminal()
    print("Program was terminated by user.\n\n")
    clear_audio_cache()
    sys.exit(1)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst.

    Args:
        lst (List[T]): The list to chunk.
        n (int): The size of each chunk.
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def utc_to_local(utc: datetime.datetime) -> datetime.datetime:
    """Convert an aware UTC datetime to a naive local datetime.

    Args:
        utc (datetime.datetime): The UTC datetime to convert.

    Returns:
        datetime.datetime: The local datetime.
    """
    return datetime.datetime.fromtimestamp(utc.timestamp())


class Cache:
    subjects = {}
    client = None

    @classmethod
    def get_subject(cls, subject_id: int):
        subject = cls.subjects.get(subject_id)
        if not subject and cls.client:
            cls.client._subject_per_ids([subject_id])
            subject = cls.subjects.get(subject_id)
        if not subject:
            raise ValueError(f"Subject {subject_id} not found.")
        return subject

    @classmethod
    def set_subject(cls, subject):
        cls.subjects[subject.id] = subject


class ClientOptions:
    """Client options."""

    def __init__(
        self,
        autoplay: bool = False,
        silent: bool = False,
        voice_mode: VoiceMode = VoiceMode.ALTERNATE,
        hard_mode: bool = False,
        dry_run: bool = False,
        limit: int = 50,
        display_mnemonics: bool = False,
        double_check: bool = False,
        test_ids: list = None,
    ):
        """Initialize the client options.

        Args:
            autoplay (bool): Whether to autoplay audio.
            silent (bool): Whether to silence the output.
            voice_mode (VoiceMode): The voice mode to use.
            hard_mode (bool): Whether to use hard mode.
            dry_run (bool): Whether to run in dry run mode.
            limit (int): The number of subjects to review.
            display_mnemonics (bool): Whether to display mnemonics.
            double_check (bool): Whether wrong meanings can be marked correct.
            test_ids (list): Subject ids to use instead of the summary.
        """
        self.autoplay = autoplay
        self.silent = silent
        self.voice_mode = voice_mode
        self.hard_mode = hard_mode
        self.dry_run = dry_run
        self.limit = limit
        self.display_mnemonics = display_mnemonics
        self.double_check = double_check
        self.test_ids = test_ids


class Client:
    """The main client class.

    Usage:
        >>> import hebikani
        >>> client = hebikani.Client('API_KEY')
    """

    def __init__(self, api_key: str, options: ClientOptions = None):
        """Initialize the client.

        Args:
            api_key (str): The API key to use.
            options (ClientOptions): The client options .
        """
        self.api_key = api_key
        self.options = options or ClientOptions()
        # Cache the client to use it in external class
        Cache.client = self

    def _load_subject_cache(self):
        """Load the subject cache."""
        subjects = load_settings("subjects.json")
        if subjects:
            spinner = Halo(text="Loading cache", spinner="dots")
            spinner.start()
            for subject in subjects:
                Cache.set_subject(Subject(subject))
            spinner.stop()
            print("Cache loaded.")
        else:
            print("No subject cache found.")

    def summary(self):
        """Get a summary of the user's current progress."""
        data = api_request(HTTPMethod.GET, "summary", self.api_key)
        return Summary(data)

    def reviews(self):
        """Start a review session with the reviews available now."""
        self._start_session(ReviewSession, "reviews")

    def lessons(self):
        """Start a lesson session with the lessons available now."""
        self._start_session(LessonSession, "lessons")

    def _start_session(self, session_class, summary_attribute: str):
        """Build the subjects from the test ids or the summary and start a session."""
        self._load_subject_cache()
        subject_ids = self.options.test_ids or getattr(
            self.summary(), summary_attribute
        )
        session_class(self, self._subject_per_ids(subject_ids)).start()

    def _fetch_pages(self, endpoint: str, **kwargs) -> Iterator[dict]:
        """Yield every page of a paginated endpoint, following next_url."""
        data = api_request(HTTPMethod.GET, endpoint, self.api_key, **kwargs)
        while data:
            yield data
            next_url = data["pages"]["next_url"]
            data = (
                api_request(HTTPMethod.GET, next_url, self.api_key)
                if next_url
                else None
            )

    def download(self):
        """Download data from the WaniKani API to have them offline."""
        subjects = load_settings("subjects.json")
        last_download = setting_modified_date("subjects.json")
        if last_download:
            date_str = last_download.strftime("%a, %d %b %Y %H:%M:%S")
            print(
                f"Subject data already cached. (Updated on {date_str}).\n"
                "Only downloading new data."
            )

        spinner = Halo(text="Downloading", spinner="dots")
        spinner.start()
        new_subjects = []
        for page in self._fetch_pages("subjects", modified_since=last_download):
            new_subjects += page["data"]
            spinner.text = f"Downloading {len(new_subjects)} subjects"
        spinner.stop()

        if not new_subjects:
            print("No new data to download.")
            return

        print(f"Downloaded {len(new_subjects)} subjects.")

        if not subjects:
            subjects = new_subjects
        else:
            subject_ids_index = {s["id"]: i for i, s in enumerate(subjects)}
            nb_modified = 0
            for new_subject in new_subjects:
                i = subject_ids_index.get(new_subject["id"])
                if i is None:
                    subjects.append(new_subject)
                else:
                    subjects[i] = new_subject
                    nb_modified += 1

            print(f"Added {len(new_subjects) - nb_modified} subjects.")
            print(f"Modified {nb_modified} subjects.")

        save_settings("subjects.json", subjects)

    def _subject_per_ids(self, subject_ids: List[int]):
        """Get subjects by ID, downloading the ones missing from the cache.

        Args:
            subject_ids (List[int]): A list of subject IDs to get.
        """
        missing_ids = set(subject_ids) - set(Cache.subjects)
        if missing_ids:
            ids = ",".join(str(i) for i in missing_ids)
            for page in self._fetch_pages(f"subjects?ids={ids}"):
                for data in page["data"]:
                    Cache.set_subject(Subject(data))

        return [Cache.get_subject(i) for i in subject_ids]

    def _assignment_id_per_subject_id(self, subject_id: int) -> int:
        """Get assignments by subject ID.

        Args:
            subject_id (int): The subject ID to get assignment for.

        Returns:
            int: The assignment ID.
        """
        data = api_request(
            HTTPMethod.GET, f"assignments?subject_ids={str(subject_id)}", self.api_key
        )
        if not data["data"]:
            raise ValueError(f"No assignment found for subject {subject_id}.")
        return int(data["data"][0]["id"])


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
        return ".mp3" if self.data["content_type"] == "audio/mpeg" else ".ogg"

    @property
    def voice_gender(self) -> Gender:
        """The gender of the voice actor."""
        gender = self.data["metadata"]["gender"]
        return Gender.MALE if gender == Gender.MALE else Gender.FEMALE

    def download(self):
        """Download the audio if not cached."""
        if self.url not in audio_cache:
            r = requests.get(self.url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            # delete=False avoids permission errors on windows.
            f = tempfile.NamedTemporaryFile(suffix=self.ext, delete=False)
            f.write(r.content)
            f.close()
            # Metadata prevents playsound from playing the file on windows.
            if system() == "Windows":
                mp3 = MP3(f.name)
                mp3.delete()
                mp3.save()
            audio_cache[self.url] = f

    def play(self):
        """Download and Play the audio."""
        self.download()
        f = audio_cache[self.url]
        threading.Thread(target=playsound, args=(f.name,), daemon=True).start()


class Summary(APIObject):
    """The summary of the user's current progress."""

    def __str__(self) -> str:
        return f"""Summary:
    Lessons: {self.nb_lessons}
    Reviews: {self.nb_reviews}
    Next reviews: {self.next_reviews_info or 'No more reviews for today'}"""

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

    @property
    def next_reviews_info(self) -> str:
        """Get the next reviews info."""
        hist_data = []
        for review in self.data["data"]["reviews"][1:]:
            nb_reviews = len(review["subject_ids"])

            if nb_reviews == 0:
                continue
            review_time = utc_to_local(
                datetime.datetime.fromisoformat(
                    review["available_at"].replace("Z", "+00:00")
                )
            )

            if datetime.datetime.today().date() != review_time.date():
                continue

            hist_data += [(review_time, nb_reviews)]

        return hist(
            hist_data,
            width=30,
            total=self.nb_reviews,
            linesep="\n\t",
        )


class ContextSentence(APIObject):
    """Context Setence object from WaniKani"""

    @property
    def en(self) -> str:
        """The english sentence.

        Returns:
            str: The english sentence.
        """
        return self.data["en"]

    @property
    def ja(self) -> str:
        """The japanese sentence.

        Returns:
            str: The japanese sentence.
        """
        return self.data["ja"]


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
        return self.data.get("type", "vocabulary")


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
    def hard_mode_acceptable_answers(self) -> List[Answer]:
        """Get the acceptable answers in hard mode.
        Katakana reading questions do not accept hiraganas.

        Returns:
            List[Answer]: The acceptable answers.
        """
        answers = self.acceptable_answers

        # Check for reading questions with two readings.
        if self.question_type == QuestionType.READING and len(answers) == 2:
            roma1 = romkan.to_roma(answers[0].value)
            roma2 = romkan.to_roma(answers[1].value)

            # Check if the two readings are the same in romaji.
            if roma1 == roma2:
                katakana_regexp = re.compile(r"[\u30A0-\u30FF]+")
                # Keep the one that has katakana characters.
                answers = [
                    answers[0]
                    if katakana_regexp.match(answers[0].value)
                    else answers[1]
                ]

        return answers

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

    def solve(self, inputed_answer: str, hard_mode: bool = False) -> AnswerType:
        """Check whether an answer is correct."""
        inputed_answer = inputed_answer.lower().strip()
        acceptable = [a.value for a in self.acceptable_answers]
        unacceptable = {a.value for a in self.unacceptable_answers}

        # In hard mode every reading must be given, separated by commas.
        if hard_mode and self.question_type == QuestionType.READING:
            answers = [i.strip() for i in inputed_answer.split(",")]
            expected = {a.value for a in self.hard_mode_acceptable_answers}
            if set(answers) == expected:
                return AnswerType.CORRECT
            if len(answers) == len(expected) and set(answers) <= (
                expected | unacceptable
            ):
                return AnswerType.INEXACT
            return AnswerType.INCORRECT

        if inputed_answer in acceptable:
            return AnswerType.CORRECT
        # Close matches are only tolerated for meanings.
        if self.question_type == QuestionType.MEANING and get_close_matches(
            inputed_answer, acceptable, cutoff=RATIO_CLOSE_MATCHES
        ):
            return AnswerType.A_BIT_OFF
        if inputed_answer in unacceptable:
            return AnswerType.INEXACT
        return AnswerType.INCORRECT


class ReviewUpdate:
    """Reviews log all the correct and incorrect answers provided through the
    'Reviews' section of WaniKani. Review records are created when a user answers
    all the parts of a subject correctly once; some subjects have both meaning
    or reading parts, and some only have one or the other.
    Note that reviews are not created for the quizzes in lessons."""

    def __init__(
        self,
        client: Client,
        subject_id: int,
        incorrect_meaning_answers: int,
        incorrect_reading_answers: int,
    ):
        """Initialize the review update.

        Args:
            client (Client): The client to use.
            subject_id (int): The subject id.
            incorrect_meaning_answers (int): The number of incorrect meaning answers.
            incorrect_reading_answers (int): The number of incorrect reading answers.
        """
        self.client = client
        self.subject_id = subject_id
        self.incorrect_meaning_answers = incorrect_meaning_answers
        self.incorrect_reading_answers = incorrect_reading_answers

    def save(self) -> dict:
        """Save the review update on WaniKani.

        Returns:
            dict: The response from the API.
        """
        request_data = None
        data = {
            "review": {
                "subject_id": self.subject_id,
                "incorrect_meaning_answers": self.incorrect_meaning_answers,
                "incorrect_reading_answers": self.incorrect_reading_answers,
            }
        }
        if self.client.options.dry_run is False:
            request_data = api_request(
                HTTPMethod.POST, "reviews", self.client.api_key, data
            )

        return request_data


class AssignmentUpdate:
    """Mark the assignment as started, moving the assignment from the lessons queue
    to the review queue. Returns the updated assignment."""

    def __init__(
        self,
        client: Client,
        subject_id: int,
    ):
        """Initialize the review update.

        Args:
            client (Client): The client.
            subject_id (int): The subject id.
        """
        self.client = client
        self.subject_id = subject_id
        self.assignment_id = self.client._assignment_id_per_subject_id(subject_id)

    def save(self):
        """Send the data to on WaniKani."""
        if self.client.options.dry_run is False:
            api_request(
                HTTPMethod.PUT,
                f"assignments/{str(self.assignment_id)}/start",
                self.client.api_key,
            )


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
        if self.object != SubjectObject.VOCABULARY:
            return []
        audios = [Audio(data) for data in self.data["data"]["pronunciation_audios"]]
        return [audio for audio in audios if audio.ext == ".mp3"]

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
        for image in self.data["data"]["character_images"]:
            if image.get("content_type") == "image/svg+xml" and image.get("url"):
                return url_to_ascii(image["url"])
        return None

    @property
    def readings(self):
        """Get the reading of the kanji."""
        if self._readings is None:
            self._readings = AnswerManager(
                [
                    Answer(answer, QuestionType.READING)
                    for answer in self.data["data"].get(
                        "readings",
                        [
                            {
                                "primary": True,
                                "reading": self.data["data"]["characters"],
                                "accepted_answer": True,
                            }
                        ],
                    )
                ]
            )
        return self._readings

    @property
    def _single_kanji(self):
        """The kanji a one character vocabulary is made of, if any.
        Its answers are tolerated as inexact instead of wrong.
        """
        if (
            self.object == SubjectObject.VOCABULARY
            and len(self.characters) == 1
            and self.component_subject_ids
        ):
            return Cache.get_subject(self.component_subject_ids[0])
        return None

    @property
    def auxiliary_readings(self):
        kanji = self._single_kanji
        return kanji.readings if kanji else None

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
    def auxiliary_meanings(self):
        kanji = self._single_kanji
        return kanji.meanings if kanji else None

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

    @property
    def reading_mnemonic(self) -> str:
        """Get the reading mnemonic.

        Returns:
            str: The reading mnemonic.
        """
        return self.data["data"]["reading_mnemonic"]

    @property
    def meaning_mnemonic(self) -> str:
        """Get the meaning mnemonic.

        Returns:
            str: The meaning mnemonic.
        """
        return self.data["data"]["meaning_mnemonic"]

    @property
    def context_sentences(self) -> List[ContextSentence]:
        """Get the context sentences.

        Returns:
            List[ContextSentence]: The context sentences.
        """
        return [
            ContextSentence(s) for s in self.data["data"].get("context_sentences", [])
        ]

    @property
    def component_subject_ids(self) -> List[int]:
        """Get the component subject ids.

        Returns:
            List[int]: The component subject ids.
        """
        return self.data["data"].get("component_subject_ids", [])


class Question:
    """The question."""

    def __init__(self, subject: Subject, question_type: QuestionType):
        """Initialize the question.

        Args:
            subject (Subject): The subject.
            question_type (QuestionType): The question type.
        """
        self.subject = subject
        self.question_type = question_type
        self.wrong_answer_count = 0
        self.solved = False

    @property
    def is_reading(self) -> bool:
        return self.question_type == QuestionType.READING

    @property
    def answers(self) -> AnswerManager:
        """Get the answers of the question."""
        return self.subject.readings if self.is_reading else self.subject.meanings

    def solve(self, inputed_answer: str, hard_mode: bool = False) -> AnswerType:
        """Check whether an answer is correct.

        Args:
            inputed_answer (str): The inputed answer.
            hard_mode (bool): Whether all the readings are required.

        Returns:
            AnswerType: The answer type.
        """
        answer = self.answers.solve(inputed_answer, hard_mode)

        # A kanji answer given for its vocabulary is inexact rather than wrong.
        # Hard mode readings do not get this tolerance.
        if answer == AnswerType.INCORRECT and not (hard_mode and self.is_reading):
            auxiliary = (
                self.subject.auxiliary_readings
                if self.is_reading
                else self.subject.auxiliary_meanings
            )
            if auxiliary:
                answer = auxiliary.solve(inputed_answer)
                if answer == AnswerType.CORRECT:
                    answer = AnswerType.INEXACT

        return answer

    def add_wrong_answer(self):
        """Add a wrong answer.
        Used when a user tags his answer as wrong.
        """
        self.wrong_answer_count += 1

    @property
    def answer_values(self):
        """Get the answer values."""
        return self.answers.answer_values

    @property
    def primary(self) -> Answer:
        """Get the primary answer."""
        return self.answers.primary

    @property
    def mnemonic(self) -> str:
        """Get the mnemonic."""
        if self.is_reading:
            return self.subject.reading_mnemonic
        return self.subject.meaning_mnemonic


class Session:
    """The session. Base class for Reviews and Lessons."""

    def __init__(self, client: Client, subjects: List[Subject]):
        """Initialize the session.

        Args:
            client (Client): The client.
            subjects (List[Subject]): The subjects.
        """
        self.client = client
        self.subjects = subjects
        self.last_audio_played = None

    def select_audio(self, audios: List[Audio]) -> Audio:
        """Select the audio to play.

        Args:
            audios (List[Audio]): The audios.

        Returns:
            Audio: The audio to play.
        """
        cached_audios = [a for a in audios if a.url in audio_cache]
        if cached_audios:
            return cached_audios[0]

        # Alternate mode starts with a random voice actor then alternates genders.
        voice_mode = self.client.options.voice_mode
        preferred_gender = {
            VoiceMode.FEMALE: Gender.FEMALE,
            VoiceMode.MALE: Gender.MALE,
        }.get(voice_mode)
        if voice_mode == VoiceMode.ALTERNATE and self.last_audio_played:
            last_gender = self.last_audio_played.voice_gender
            preferred_gender = (
                Gender.MALE if last_gender == Gender.FEMALE else Gender.FEMALE
            )

        candidates = [a for a in audios if a.voice_gender == preferred_gender]
        return candidates[0] if candidates else random.choice(audios)

    def play_audio(self, subject: Subject):
        """Play one of the subject audios and remember it for alternate mode."""
        audio = self.select_audio(subject.audios)
        audio.play()
        self.last_audio_played = audio


class QuestionQueue(list):
    """Handle queue."""

    def shuffle(self):
        """Shuffle the queue."""
        random.shuffle(self)

    def rebuild(self, subjects: List[Subject]):
        """Fill the queue with up to MAX_QUEUE_SIZE subjects taken from `subjects`.

        Args:
            subjects (List[Subject]): The subjects left to add. Consumed in place.
        """
        nb_queue_subjects = len({question.subject for question in self})

        while nb_queue_subjects < MAX_QUEUE_SIZE and subjects:
            self.extend(subjects.pop(0).questions)
            nb_queue_subjects += 1

        self.shuffle()


class ReviewSession(Session):
    """A review session."""

    def __init__(
        self, client: Client, subjects: List[Subject], from_lesson: bool = False
    ):
        """Initialize the review session.

        Args:
            client (Client): The client.
            subjects (List[Subject]): The subjects.
        """
        super().__init__(client, subjects)
        self.subjects = self.subjects[: client.options.limit]
        self.from_lesson = from_lesson
        self.nb_subjects = len(self.subjects)
        self.nb_correct_answers = 0
        self.nb_incorrect_answers = 0  # Multiple error count multiple times.
        self.nb_completed_subjects = 0
        self.queue = QuestionQueue()

    @property
    def correct_rate(self) -> str:
        total_answers = self.nb_incorrect_answers + self.nb_correct_answers
        if total_answers == 0:
            return "X"
        return f"{round(self.nb_correct_answers * 100 / total_answers, 2)}%"

    def start(self):
        """Start the reviews.

        Questions are asked one by one from the queue. A correct answer removes
        the question, a wrong one shows the answer and puts it back at the end.
        """
        clear_terminal()

        print(
            "\nReview session started.\n"
            "The session will end when you have answered all the questions.\n"
            "Questions are submitted automatically when both reading and "
            "meaning have been answer for a same subject.\n"
            "You can quit the session at any time by typing 'ctrl + c'.\n\n"
            f"This session contains {self.nb_subjects} subjects.\n"
        )

        input("Press enter to start the session...")

        self.queue.rebuild(self.subjects)

        while self.queue:
            question = self.queue.pop(0)
            clear_terminal()
            print(
                f"Total Reviews {self.nb_completed_subjects}/{self.nb_subjects}",
                f"- {self.correct_rate}:\n",
            )
            print(question.subject.characters + "\n")

            # Loop on inexact answers (e.g. onyomi given for a kunyomi question).
            # They are not mistakes, the user is asked again.
            answer_type = None
            while answer_type is None or answer_type == AnswerType.INEXACT:
                answer_type = self.ask_answer(question)
                self.process_answer(question, answer_type)

            self.process_subject(question.subject)

            self.ask_audio(question)
            input("\nPress enter to continue...")

        print("\n\nReviews are done!")

    def _mark_correct(self, question: Question):
        self.nb_correct_answers += 1
        question.solved = True

    def _mark_wrong(self, question: Question):
        self.nb_incorrect_answers += 1
        question.add_wrong_answer()
        # Shuffle before appending so the question does not come twice in a row.
        self.queue.shuffle()
        self.queue.append(question)

    def process_answer(self, question: Question, answer_type: AnswerType):
        """Update the counters and the queue according to the answer.

        Args:
            question (Question): The question.
            answer_type (AnswerType): The answer type.
        """
        if answer_type == AnswerType.CORRECT:
            print("\nCorrect!")
            self._mark_correct(question)

        elif answer_type == AnswerType.A_BIT_OFF:
            print(
                "Your answer is a bit off.",
                f"The correct answer is: {question.answer_values}",
            )
            if input("Do you want to validate your answer? (Y/n) ") in ["n", "N"]:
                self._mark_wrong(question)
            else:
                self._mark_correct(question)

        elif answer_type == AnswerType.INEXACT:
            print(
                "\nTry again. We are looking for the",
                f"{question.primary.type}.\n",
            )

        else:
            print("\nWrong ! The correct answer is:", question.answer_values)

            answer_was_correct = "N"
            if not question.is_reading and self.client.options.double_check:
                time.sleep(0.5)
                answer_was_correct = input("My answer was correct [y/N] ")

            if answer_was_correct in ["y", "Y"]:
                print("Question was changed to correct")
                self._mark_correct(question)
            else:
                self._mark_wrong(question)
                if self.client.options.display_mnemonics:
                    print(f"\nMnemonic: {wanikani_tag_to_color(question.mnemonic)}")

    def process_subject(self, subject: Subject):
        """Submit the subject to WaniKani once all its questions are solved.

        Args:
            subject (Subject): The subject.
        """
        if not subject.solved:
            return

        self.nb_completed_subjects += 1
        if self.from_lesson:
            AssignmentUpdate(self.client, subject.id).save()
            return

        reading_question = subject.reading_question
        ReviewUpdate(
            self.client,
            subject.id,
            subject.meaning_question.wrong_answer_count,
            reading_question.wrong_answer_count if reading_question else 0,
        ).save()
        # Refill the queue with the next subjects. Lessons are quizzed by batch
        # so they never need it.
        self.queue.rebuild(self.subjects)

    def ask_answer(self, question: Question):
        """Ask the user for an answer.

        Args:
            question (Question): The question.

        Returns:
            AnswerType: The answer type.
        """
        prompt = (
            f"{question.subject.object.replace('_', ' ')} - {question.question_type}"
        )

        # Hard mode shows how many readings are expected. Some kanji require
        # several (e.g. 谷: たに、や) while their vocabulary only needs one (たに).
        if question.is_reading and self.client.options.hard_mode:
            nb_answers = len(question.subject.readings.hard_mode_acceptable_answers)
            prompt += f" ({nb_answers} {'answer' if nb_answers == 1 else 'answers'})"
        prompt += ": "

        if question.is_reading:
            try:
                inputed_answer = input_kana(prompt)
            except KeyboardInterrupt:
                handler()
        else:
            inputed_answer = ""
            while not inputed_answer:
                inputed_answer = input(prompt)
                if not inputed_answer:
                    print("\a")

        return question.solve(inputed_answer, self.client.options.hard_mode)

    def ask_audio(self, question: Question):
        """Ask the user if they want to hear the audio.

        Args:
            question (Question): The question.
        """
        if (
            not self.client.options.silent
            and question.is_reading
            and question.subject.audios
            and (
                self.client.options.autoplay
                or input("\nWould you like to hear the audio? [y/N] ") in ["y", "Y"]
            )
        ):
            self.play_audio(question.subject)


TABS_PER_OBJECT = {
    SubjectObject.RADICAL: ["meaning"],
    SubjectObject.KANJI: ["composition", "meaning", "reading"],
    SubjectObject.VOCABULARY: ["composition", "meaning", "reading", "context"],
    SubjectObject.KANA_VOCABULARY: ["meaning"],
}


class LessonSession(Session):
    """A lesson session."""

    def start(self):
        """Start the Lesson session.

        We start by showing the subjects to the user by batch.
        Once the user is done, we start a review session.
        We repeat this process until the user is done.
        """
        clear_terminal()
        print(
            "Lesson session started.\n"
            "You will first be shown a batch of new subjects.\n"
            "You will then be asked to review the subjects.\n"
            "Lesson progress will be submitted to WaniKani "
            "when answering the questions.\n"
            "Quitting the session will not affect your progress.\n"
            "You can quit the session at any time by typing 'ctrl + c'.\n\n"
        )

        input("Press enter to start the session...")

        nb_lessons = len(self.subjects)
        nb_completed_lessons = 0

        for batch in chunks(self.subjects, LESSON_BATCH_SIZE):
            for subject in batch:
                self.lesson_interface(subject)

            ReviewSession(self.client, batch, from_lesson=True).start()
            nb_completed_lessons += len(batch)
            print(f"\nLessons: {nb_completed_lessons}/{nb_lessons}")

            if nb_completed_lessons < nb_lessons:
                input("\nPress enter to continue...")

    def lesson_interface(self, subject: Subject):
        """Show the subjects to the user with a nice CLI interface.

        Args:
            subject (Subject): The subject.
        """
        tabs = TABS_PER_OBJECT[subject.object]
        tab_index = 0
        if subject.audios and not self.client.options.silent:
            self.select_audio(subject.audios).download()

        while 0 <= tab_index < len(tabs):
            clear_terminal()
            print(
                f"{subject.object.capitalize().replace('_', ' ')}:"
                f"\n\n{subject.characters}\n"
            )
            print(self.beautify_tabs_display(tabs, tab_index))
            print("\n")
            print(getattr(self, f"tab_{tabs[tab_index]}")(subject))
            print("\nPress directional keys to navigate the tabs.")

            tab_index += self.read_navigation_key()
            tab_index = max(tab_index, 0)

    @staticmethod
    def read_navigation_key() -> int:
        """Wait for enter, right or left and return the tab offset."""
        while True:
            key = ord(getch(use_raw_input=False))
            if key in KEYS_ENTER + KEYS_RIGHT:
                return 1
            if key in KEYS_LEFT:
                return -1

    def tab_composition(self, subject: Subject) -> str:
        """Show the composition tab.

        Args:
            subject (Subject): The subject.

        Returns:
            str: The tab content.
        """
        res = ""
        if subject.component_subject_ids:
            subjects = self.client._subject_per_ids(subject.component_subject_ids)
            res = (
                f"This {subject.object.replace('_', ' ')} is made of "
                + f"{len(subjects)} {subjects[0].object}"
                + ":\n"
                + "\n".join(
                    f"- {s.characters}: {s.meanings.primary.value}" for s in subjects
                )
            )

        return res

    def tab_meaning(self, subject: Subject) -> str:
        """Show the meaning tab.

        Args:
            subject (Subject): The subject.

        Returns:
            str: The tab content.
        """
        return (
            subject.meanings.answer_values
            + "\n\n"
            + wanikani_tag_to_color(subject.meaning_mnemonic)
        )

    def tab_reading(self, subject: Subject) -> str:
        """Show the reading tab.

        Args:
            subject (Subject): The subject.

        Returns:
            str: The tab content.
        """
        if subject.audios and not self.client.options.silent:
            self.play_audio(subject)

        return (
            subject.readings.answer_values
            + "\n\n"
            + wanikani_tag_to_color(subject.reading_mnemonic)
        )

    def tab_context(self, subject: Subject) -> str:
        """Show the context tab.

        Args:
            subject (Subject): The subject.

        Returns:
            str: The tab content.
        """
        return "\n\n".join([f"{s.ja}\n{s.en}" for s in subject.context_sentences])

    def beautify_tab_name(self, tab_name: str) -> str:
        """Human readable tab name."""
        return tab_name.replace("_", " ").capitalize()

    def beautify_tabs_display(self, tabs: List[str], tab_index: int) -> str:
        """Beautify the tabs display.

        Args:
            tabs (List[str]): The tabs.
            tab_index (int): The tab index.

        Returns:
            str: The beautified tabs display.
        """
        _tabs = []
        for i, tab in enumerate(tabs):
            name = self.beautify_tab_name(tab)
            if i == tab_index:
                name = Style.BRIGHT + Back.BLUE + Fore.WHITE + name

            _tabs.append(name)

        return (
            (Style.RESET_ALL + Back.RESET + Fore.RESET + " > ").join(_tabs)
            + Style.RESET_ALL
            + Back.RESET
            + Fore.RESET
        )


def build_parser() -> ArgumentParser:
    """Build the command line parser."""
    # Public Client methods are the available modes.
    commands = [x for x in dir(Client) if not x.startswith("_")]
    command_str = ", ".join(commands[:-1]) + " or " + commands[-1]

    parser = ArgumentParser(
        description="A Python client for the Wanikani API.",
        formatter_class=RawTextHelpFormatter,
    )

    text = "The mode in which HebiKani will run. Must be " + command_str

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
        "- Ask for all the readings separated with a comma.\n"
        "E.g: The answer for 何　should be 'なん,なに'. "
        "The order does not matter. "
        "\n- Questions using katakana can only be answered "
        "with katanana.\n"
        "E.g:　The anwser for ベッドの下 should be ベッドのした."
        "\n(default: False)"
    )

    parser.add_argument("--hard", action="store_true", default=False, help=text)

    text = (
        "Do not submit answers to the WaniKani API."
        "This mode is meant for testing purposes."
    )

    parser.add_argument("--dry-run", action="store_true", default=False, help=text)

    text = "Number of subjects to review per session. (default: 50, max: 500)"

    parser.add_argument("--limit", type=range_int_type, default=50, help=text)

    text = "Display mnemonic when an answer is wrong. (default: False)"

    parser.add_argument("--mnemonics", action="store_true", default=False, help=text)

    text = (
        "Give you the chance the answer as correct for meaning (only). (default: False)"
    )

    parser.add_argument(
        "--double-check", "--db", action="store_true", default=False, help=text
    )

    text = (
        "Test specific lessons or reviews using the subject ids. E.g 41,50,200. "
        "Implies --dry-run."
    )
    parser.add_argument("--test-ids", help=text, default="")

    return parser


def main():
    """Run the client."""
    parser = build_parser()
    args = parser.parse_args()

    if args.api_key is None:
        parser.error("api_key is required.")

    client_options = ClientOptions(
        autoplay=args.autoplay,
        silent=args.silent,
        voice_mode=args.voice,
        hard_mode=args.hard,
        dry_run=args.dry_run or bool(args.test_ids),
        limit=args.limit,
        display_mnemonics=args.mnemonics,
        double_check=args.double_check,
        test_ids=[int(i) for i in args.test_ids.split(",")] if args.test_ids else [],
    )

    client = Client(args.api_key, options=client_options)

    signal(SIGINT, handler)
    try:
        res = getattr(client, args.mode)()
        # Sessions print as they go and return nothing.
        if res:
            print(res)
    except Exception as e:
        print(e)

    clear_audio_cache()


def range_int_type(arg: str) -> int:
    """Type function for argparse - an int within some predefined bounds

    Args:
        arg (str): The value of the argument.

    Returns:
        int: The parsed value.

    Raises:
        argparse.ArgumentTypeError: If the value is not within the bounds.
    """
    try:
        arg = int(arg)
    except ValueError:
        raise ArgumentTypeError("Must be an integer")
    if not MIN_NB_SUBJECTS <= arg <= MAX_NB_SUJECTS:
        raise ArgumentTypeError(
            f"Argument must be between {MIN_NB_SUBJECTS} and {MAX_NB_SUJECTS}"
        )
    return arg


if __name__ == "__main__":
    main()
