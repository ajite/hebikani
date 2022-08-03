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
import tempfile
import threading
import time
from argparse import ArgumentParser, ArgumentTypeError, RawTextHelpFormatter
from difflib import get_close_matches
from io import BytesIO
from platform import system
from signal import SIGINT, signal
from typing import List

import ascii_magic
import requests
import romkan
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

if system() == "Windows":
    from mutagen.mp3 import MP3

API_URL = "https://api.wanikani.com/v2/"
MIN_NB_SUBJECTS = 1
MAX_NB_SUJECTS = 500

# Number of subjects inside a session queue at once.
MAX_QUEUE_SIZE = 10

# Ratio when using difflib.get_close_matches()
RATIO_CLOSE_MATCHES = 0.8

# Cache audio during session to avoid redownloading the same audio
audio_cache = {}


def api_request(method: HTTPMethod, endpoint: str, api_key: str, json=None) -> dict:
    """Make an API request with correct headers.

    Args:
        method (HTTPMethod): The HTTP method to use.
        endpoint (str): The endpoint to make the request to.
        api_key (str): The API key to use.
        json (dict): The data to send.

    Returns:
        dict: The response from the API.

    Raises:
        ValueError: If the method is not a valid HTTP method.
    """
    url = API_URL + endpoint
    headers = {"Authorization": f"Bearer {api_key}"}
    if method == HTTPMethod.GET:
        resp = requests.get(url, headers=headers)
    elif method == HTTPMethod.POST or method == HTTPMethod.PUT:
        json = json or {}  # In case json is None
        resp = getattr(requests, method.lower())(url, headers=headers, json=json)
    else:
        raise ValueError("Invalid HTTP method")
    if resp.status_code == 401:
        raise ValueError("Invalid API Key")

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
    """Clear the audio cache."""
    for audio_file in audio_cache.values():
        os.unlink(audio_file.name)


def handler(signal_received=None, frame=None):
    """Terminate the program gracefully."""
    clear_terminal()
    print("Program was terminated by user.\n\n")
    clear_audio_cache()
    exit(1)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst.

    Args:
        lst (List[T]): The list to chunk.
        n (int): The size of each chunk.4
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def utc_to_local(utc: datetime.datetime) -> datetime.datetime:
    """Convert a UTC datetime to local datetime.

    Args:
        utc (datetime.datetime): The UTC datetime to convert.

    Returns:
        datetime.datetime: The local datetime.
    """
    epoch = time.mktime(utc.timetuple())
    offset = datetime.datetime.fromtimestamp(
        epoch
    ) - datetime.datetime.utcfromtimestamp(epoch)
    return utc + offset


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
        """
        self.autoplay = autoplay
        self.silent = silent
        self.voice_mode = voice_mode
        self.hard_mode = hard_mode
        self.dry_run = dry_run
        self.limit = limit
        self.display_mnemonics = display_mnemonics
        self.double_check = double_check


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
        self._subject_cache = {}

    def summary(self):
        """Get a summary of the user's current progress."""
        data = api_request(HTTPMethod.GET, "summary", self.api_key)
        return Summary(data)

    def reviews(self):
        """Get reviews for a subject.

        Args:
            subject_id (int): The subject ID to get reviews for.
        """
        subjects = self._subject_per_ids(self.summary().reviews)
        session = ReviewSession(self, subjects)
        session.start()

    def lessons(self):
        """Get lessons from the WaniKani API."""
        subjects = self._subject_per_ids(self.summary().lessons)
        session = LessonSession(self, subjects)
        session.start()

    def _subject_per_ids(self, subject_ids: List[int]):
        """Get subjects by ID.

        Args:
            subject_ids (List[int]): A list of subject IDs to get.
        """
        # Remove subjects that are already in the cache
        missing_ids = list(set(subject_ids) - set(self._subject_cache.keys()))
        if missing_ids:
            ids = ",".join(str(i) for i in missing_ids)
            data = api_request(HTTPMethod.GET, f"subjects?ids={ids}", self.api_key)

            for data in data["data"]:
                subject = Subject(data)
                self._subject_cache[subject.id] = subject

        return [self._subject_cache[i] for i in subject_ids]

    def _assignment_id_per_subject_id(self, subject_id: int) -> int:
        """Get assignments by subject ID.

        Args:
            subject_id (int): The subject ID to get assignment for.

        Returns:
            int: The assignment ID.
        """
        assignment_id = None
        data = api_request(
            HTTPMethod.GET, f"assignments?subject_ids={str(subject_id)}", self.api_key
        )
        if data["data"]:
            assignment_id = data["data"][0]["id"]
        return int(assignment_id)


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

    def download(self):
        """Download the audio if not cached."""
        if self.url not in audio_cache.keys():
            r = requests.get(self.url)
            # We have to use delete is false otherwise we have permission
            # error on windows
            f = tempfile.NamedTemporaryFile(suffix=self.ext, delete=False)
            f.write(r.content)
            f.seek(0)
            f.close()
            # Remove metadata in windows
            # It prevents playsound to playfile
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
        bins = 0
        for review in self.data["data"]["reviews"][1:]:
            nb_reviews = len(review["subject_ids"])

            if nb_reviews == 0:
                continue
            review_time = datetime.datetime.fromisoformat(
                review["available_at"].replace("Z", "+00:00")
            )
            review_time = utc_to_local(review_time).replace(tzinfo=None)

            if datetime.datetime.today().date() != review_time.date():
                continue

            bins += 1
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

    def solve(self, inputed_answer: str, hard_mode: bool = False) -> bool:
        """Check wether an answer is correct."""
        inputed_answer = inputed_answer.lower().strip()
        answer_type = AnswerType.INCORRECT
        if hard_mode and QuestionType.READING:
            # In hard mode check that all the answers are correct.
            # Only works for reading questions.
            answer_type = AnswerType.CORRECT
            answers = [i.strip() for i in inputed_answer.split(",")]
            if set(answers) == set(
                [a.value for a in self.hard_mode_acceptable_answers]
            ):
                answer_type = AnswerType.CORRECT
            elif (
                len(self.hard_mode_acceptable_answers) == len(answers)
                and len(
                    set(answers)
                    - (
                        set([a.value for a in self.hard_mode_acceptable_answers])
                        | set([a.value for a in self.unacceptable_answers])
                    )
                )
                == 0
            ):
                answer_type = AnswerType.INEXACT
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
    def primary(self) -> Answer:
        """Get the primary answer.

        Returns:
            Answer: The primary answer.
        """
        _primary = None
        if self.question_type == QuestionType.MEANING:
            _primary = self.subject.meanings.primary
        else:
            _primary = self.subject.readings.primary

        return _primary

    @property
    def mnemonic(self) -> str:
        """Get the mnemonic."""
        _mnemonic = None
        if self.question_type == QuestionType.READING:
            _mnemonic = self.subject.reading_mnemonic
        else:
            _mnemonic = self.subject.meaning_mnemonic

        return _mnemonic


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
        audio = None

        audio_cache_urls = list(
            set(audio_cache.keys()).intersection(set([a.url for a in audios]))
        )
        # use cache
        if audio_cache_urls:
            audio = list(filter(lambda a: a.url in audio_cache_urls[0], audios))[0]
        #  In alternate mode select a random voice actor to begin with
        #  We then alternate with female and male voice actors
        elif self.client.options.voice_mode == VoiceMode.FEMALE or (
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


class QuestionQueue(list):
    """Handle queue."""

    def __init__(self) -> None:
        """Initialize the queue."""
        super().__init__()

    def shuffle(self):
        """Shuffle the queue.

        TODO implement logic to implement reordering scripts.
        The reordering script should be activated and configured
        in the client options.
        """
        random.shuffle(self)

    def rebuild(self, subjects: List[Subject]):
        """Build the queue. Add correct number of questions to the queue.
        At the initialisation, we add MAX_QUEUE_SIZE or USER LIMIT
        questions to the queue.

        Args:
            subjects (List[Subject]): The subjects.
        """
        queue_subjects = set([question.subject for question in self])
        i = len(queue_subjects)

        while i < MAX_QUEUE_SIZE and len(subjects) > 0:
            subject = subjects.pop(0)
            self.extend(subject.questions)
            i += 1

        self.nb_session_subjects = i
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
        self.nb_session_subjects = 0
        self.nb_correct_answers = 0
        self.nb_incorrect_answers = 0  # Multiple error count multiple times.
        self.nb_completed_subjects = 0
        self.nb_session_completed_subjects = 0
        self.queue = QuestionQueue()

    def start(self):
        """Start the reviews.

        We will start with the first question in the queue.
        If the user answers correctly, we will remove the question from the deck
        and move on to the next question.
        Otherwise we will show the user the correct answer, shuffle the deck
        and move on to the next card.
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
        """Start the review session."""

        self.queue.rebuild(self.subjects)

        while self.queue:
            question = self.queue.pop(0)
            clear_terminal()

            total_answers = self.nb_incorrect_answers + self.nb_correct_answers
            correct_rate = "X"
            if total_answers > 0:
                correct_rate = (
                    str(round(self.nb_correct_answers * 100 / total_answers, 2)) + "%"
                )
            print(
                f"Total Reviews {self.nb_completed_subjects}/{self.nb_subjects}",
                f"- {correct_rate}:\n",
            )
            print(question.subject.characters + "\n")
            answer_type = None

            """We use a loop in case the user answers is not wrong but not acceptable

            E.g: the question asks for the kunyomi but we wrote the onyomi.
            We do not want to fail the user because of this. It is not a mistake.
            """
            while answer_type is None or answer_type == AnswerType.INEXACT:
                answer_type = self.ask_answer(question)
                self.process_answer(question, answer_type)

            self.process_subject(question.subject)

            self.ask_audio(question)
            input("\nPress enter to continue...")

        print("\n\nReviews are done!")

    def process_answer(self, question: Question, answer_type: AnswerType):
        """Process the answer.

        Args:
            question (Question): The question.
            answer_type (AnswerType): The answer type.
        """
        # If the user answers correctly, we remove the card from the deck
        if answer_type == AnswerType.CORRECT:
            print("\nCorrect!")
            self.nb_correct_answers += 1

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
                self.nb_incorrect_answers += 1
                question.add_wrong_answer()
                self.queue.shuffle()

                # Add the question at the end of the queue
                # So we don't have it twice in a row.
                self.queue.append(question)
            else:
                self.nb_correct_answers += 1
                question.solved = True

        # If the user answers another reading, we ask the user to correct it
        elif answer_type == AnswerType.INEXACT:
            print(
                "\nTry again. We are looking for the",
                f"{question.primary.type}.",
            )
        # If the user answers incorrectly, we show the correct answer
        else:
            print(
                "\nWrong ! The correct answer is:",
                question.answer_values,
            )

            if (
                question.question_type == QuestionType.MEANING
                and self.client.options.double_check
            ):
                answer_was_correct = input("My answer was correct [y/N] ")
            else:
                answer_was_correct = "N"

            if answer_was_correct not in ["y", "Y"]:
                self.nb_incorrect_answers += 1
                self.queue.shuffle()
                # Add the question at the end of the queue
                # So we don't have it twice in a row.
                self.queue.append(question)
                if self.client.options.display_mnemonics:
                    print(f"\nMnemonic: {wanikani_tag_to_color(question.mnemonic)}")
            else:
                print("Question was changed to correct")
                self.nb_correct_answers += 1
                question.solved = True

    def process_subject(self, subject: Subject):
        """Process the subject. Set it as solved if the user answered
        all the questions correctly.

        Args:
            subject (Subject): The subject.
        """
        if subject.solved:
            self.nb_subjects -= 1
            self.nb_completed_subjects += 1
            self.nb_session_completed_subjects += 1
            if self.from_lesson:
                AssignmentUpdate(self.client, subject.id).save()
            else:
                ReviewUpdate(
                    self.client,
                    subject.id,
                    subject.meaning_question.wrong_answer_count,
                    subject.reading_question.wrong_answer_count
                    if subject.reading_question
                    else 0,
                ).save()

                # When removing an item from the queue it's important
                # to rebuild the queue.
                # It's not needed for lessons.
                self.queue.rebuild(self.subjects)

    def ask_answer(self, question: Question):
        """Ask the user for an answer.

        Args:
            question (Question): The question.

        Returns:
            AnswerType: The answer type.
        """
        prompt = f"{question.subject.object} - {question.question_type}: "

        # Display the number of answers for the question in hard mode.
        # Some kanji require multiple answers while their vocabulary only need one.
        # E.g: 谷. The readings for the kanji are: たに、や.
        # But the vocabulary only needs one answer: たに.
        if (
            question.question_type == QuestionType.READING
            and self.client.options.hard_mode
        ):
            nb_answers = len(question.subject.readings.hard_mode_acceptable_answers)
            prompt = (
                prompt[:-2]
                + f" ({nb_answers} {'answer' if nb_answers == 1 else 'answers'}): "
            )

        if question.question_type == QuestionType.MEANING:
            inputed_answer = None
            while not inputed_answer:
                inputed_answer = input(prompt)
                if not inputed_answer:
                    print("\a")
        else:
            try:
                inputed_answer = input_kana(prompt)
            except KeyboardInterrupt:
                handler()

        answer_type = question.solve(inputed_answer, self.client.options.hard_mode)
        return answer_type

    def ask_audio(self, question: Question):
        """Ask the user if they want to hear the audio.

        Args:
            question (Question): The question.
        """
        if (
            not self.client.options.silent
            and question.subject.audios
            and question.question_type == QuestionType.READING
            and (
                self.client.options.autoplay
                or input("Would you like to hear the audio? [y/N] ") in ["y", "Y"]
            )
        ):
            audio = self.select_audio(question.subject.audios)
            audio.play()
            self.last_audio_played = audio


class LessonSession(Session):
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
        batches = chunks(self.subjects, 3)

        for batch in batches:
            for subject in batch:
                clear_terminal()
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
        tab_index = 0
        while True:
            clear_terminal()
            print(f"{subject.object.capitalize()}:\n\n{subject.characters}\n")
            tabs = ["composition", "meaning", "reading", "context"]
            if (
                subject.object == SubjectObject.VOCABULARY
                and not self.client.options.silent
            ):
                # Pre download audio
                self.select_audio(subject.audios).download()
            if subject.object == SubjectObject.RADICAL:
                tabs = ["meaning"]
            elif subject.object == SubjectObject.KANJI:
                tabs = ["composition", "meaning", "reading"]

            print(self.beautify_tabs_display(tabs, tab_index))
            print("\n")
            print(getattr(self, f"tab_{tabs[tab_index]}")(subject))

            print("\nPress directional keys to navigate the tabs.")
            key = None

            # Only accept valid keys
            while key not in [10, 67, 68]:
                chr = getch(use_raw_input=False)
                key = ord(chr)
            if key == 67 or key == 10:  # Right
                # sys.stdout.write("\n")
                tab_index += 1
            elif key == 68:  # Left
                # sys.stdout.write("\n")
                tab_index -= 1

            if tab_index < 0:
                tab_index = 0
            elif tab_index > len(tabs) - 1:
                # Go to next subject
                break

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
                f"This {subject.object} is made of {len(subjects)} {subjects[0].object}"
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
            audio = self.select_audio(subject.audios)
            audio.play()
            self.last_audio_played = audio

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
        "You will need to input all the correcting meanings to",
        "validate an answer. E.g: 'なん, なん' for 何. The order does not matter.",
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
        limit=args.limit,
        display_mnemonics=args.mnemonics,
        double_check=args.double_check
    )

    client = Client(args.api_key, options=client_options)

    signal(SIGINT, handler)  # Register the SIGINT handler.
    try:
        res = getattr(client, args.mode)()
        # Do not display command that do not return a response.
        # They already have been displayed.
        if res:
            print(res)
    except Exception as e:
        print(e)

    clear_audio_cache()


def range_int_type(arg: str) -> int:
    """Type function for argparse - a int within some predefined bounds

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
        raise ArgumentTypeError("Must be a floating point number")
    if arg < MIN_NB_SUBJECTS or arg > MAX_NB_SUJECTS:
        raise ArgumentTypeError(
            "Argument must be <= "
            + str(MAX_NB_SUJECTS)
            + " and >= "
            + str(MIN_NB_SUBJECTS)
        )
    return arg


if __name__ == "__main__":
    main()
