#!/usr/bin/env python

"""
This script is the program's entry point. It currently also contains a suite of
helper functions/classes, but these will probably get refactored in the far
future.
"""

import os
import random
from argparse import ArgumentParser
from io import BytesIO

import ascii_magic
import requests
from PIL import Image, ImageOps

from wanikanicli import __version__
from wanikanicli.input import input_kana

__all__ = ['Client', 'Kanji']

API_URL = "https://api.wanikani.com/v2/"


class CardKind(enumerate):
    """Card kinds."""
    MEANING = 'meaning'
    READING = 'reading'


class CardType(enumerate):
    """Card kinds."""
    RADICAL = 'radical'
    KANJI = 'kanji'
    VOCABULARY = 'vocabulary'


def http_get(endpoint, api_key):
    """Make a GET request to the API.

    Args:
        endpoint (str): The endpoint to make the request to.
        api_key (str): The API key to use.
    """
    url = API_URL + endpoint
    headers = {'Authorization': f'Bearer {api_key}'}
    resp = requests.get(url, headers=headers)
    return resp.json()


def url_to_ascii(url):
    """Uses ascii_magic to generate an ascii art image from an image downloaded
    from a URL.
    """
    request = requests.get(url)
    downloaded_image_file = BytesIO(request.content)
    downloaded_image = Image.open(downloaded_image_file)

    # Downloaded image mode is LA.
    # Create a white rgba background
    image = Image.new("RGBA", downloaded_image.size, 'white')
    image.paste(downloaded_image, (0, 0), downloaded_image)
    image = ImageOps.invert(image.convert('RGB'))

    ascii_art = ascii_magic.from_image(image, columns=64)
    return ascii_art


def clear_terminal():
    """Clear the terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


class Client:
    """The main client class.

    Usage:
        >>> import wanikani
        >>> client = wanikani.Client('API_KEY')
    """

    def __init__(self, api_key):
        """Initialize the client.

        Args:
            api_key (str): The API key to use.
        """
        self.api_key = api_key

    def summary(self):
        """Get a summary of the user's current progress."""
        data = http_get('summary', self.api_key)
        return Summary(data)

    def reviews(self):
        """Get reviews for a subject.

        Args:
            subject_id (int): The subject ID to get reviews for.
        """
        subjects = self._subject_per_id(self.summary().reviews)
        session = ReviewSession(subjects)
        session.start()

    def lessons(self):
        """Get lessons from the wanikani server. Not currently implemented."""
        raise NotImplementedError()

    def _subject_per_id(self, subject_ids):
        """Get subjects by ID.

        Args:
            subject_ids (list): A list of subject IDs to get.
        """
        ids = ','.join(str(i) for i in subject_ids)
        data = http_get(f'subjects?ids={ids}', self.api_key)
        return [Subject(subject) for subject in data['data']]


class ReviewSession:
    """A review session."""

    def __init__(self, subjects):
        """Initialize the review session.

        Args:
            subject_id (int): The subject ID.
            session_id (int): The session ID.
            data (dict): The data.
        """
        self.queue = []
        self.build_queue(subjects)

    def build_queue(self, subjects):
        """Build the queue.

        Args:
            subjects (list): A list of subjects.
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

        while self.queue:
            card = self.queue[0]
            clear_terminal()

            total_answers = nb_incorrect_answers + nb_correct_answers
            correct_rate = ''
            if total_answers > 0:
                correct_rate = str(
                    round(nb_correct_answers * 100 / total_answers, 2)) + '%'
            print(
                f"Review {nb_correct_answers}/{len(self.queue)} - {correct_rate}:\n\n")
            print(card.front)
            if card.card_kind == CardKind.MEANING:
                answer = input(f"{card.card_type} - {card.card_kind}: ")
            else:
                answer = input_kana(f"{card.card_type} - {card.card_kind}: ")
            if card.solve(answer):
                print('Correct!')
                nb_correct_answers += 1
                del self.queue[0]
            else:
                nb_incorrect_answers += 1
                print(f"""
Wrong ! The correct answer is: {', '.join(card.back)}
""")
                self.shuffle()
            input("Press a key to continue...")

        print('All done!')


class APIObject:
    """Base class for API objects."""

    def __init__(self, data):
        """Initialize the lesson.

        Args:
            data (dict): The data to use.
        """
        self.data = data


class Summary(APIObject):
    """The summary of the user's current progress."""

    def __str__(self) -> str:
        return f"""Summary:
    Lessons: {self.nb_lessons}
    Reviews: {self.nb_reviews}"""

    @property
    def lessons(self):
        """Get the lessons available."""
        return self.data['data']['lessons'][0]['subject_ids']

    @property
    def reviews(self):
        """Get the reviews available."""
        return self.data['data']['reviews'][0]['subject_ids']

    @property
    def nb_lessons(self):
        """Get the number of lessons available."""
        return len(self.lessons)

    @property
    def nb_reviews(self):
        """Get the number of reviews available."""
        return len(self.reviews)


class Card:
    """A card."""

    def __init__(self, front, back, card_type, card_kind=CardKind.MEANING):
        """Initialize the card.

        Args:
            front (str): The front of the card.
            back (str): The back of the card.
            card_kind (CardKind): The kind of card.
        """
        self.front = front
        self.back = [text.lower() for text in back]
        self.card_type = card_type
        self.card_kind = card_kind

    def solve(self, answer):
        """Check wether an answer is correct."""
        return answer.lower() in self.back


class Radical(APIObject):
    """A radical."""

    def __str__(self):
        return f"Radical: {self.characters}"

    @property
    def characters(self):
        """Get the characters of the radical or its ascii image."""
        _characters = self.data['data']['characters']
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
        for image in self.data['data']['character_images']:
            content_type = image.get('content_type')
            dimensions = image.get('metadata', {}).get('dimensions')
            if content_type == 'image/png' and dimensions == '32x32':
                url = image.get('url')
                break

        if url:
            _ascii = url_to_ascii(url)

        return _ascii

    @property
    def meanings(self):
        """Get the meanings of the vocabulary."""
        return [meaning['meaning']
                for meaning in self.data['data']['meanings']]

    @property
    def cards(self):
        """Get the card."""
        return [Card(self.characters, self.meanings, CardType.RADICAL)]


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
    def readings(self):
        """Get the reading of the kanji."""
        return [reading['reading']
                for reading in self.data['data']['readings']]

    @property
    def characters(self):
        """Get the characters of the kanji."""
        return self.data['data']['characters']

    @property
    def cards(self):
        """Get the cards.
        Kanji and Vocabulary cards have meaning and reading.
        """
        _cards = super(Kanji, self).cards
        _cards.append(Card(self.characters, self.readings,
                      self.type, CardKind.READING))
        return _cards


class Vocabulary(Kanji):
    """A vocabulary"""
    @property
    def type(self):
        """Get the type."""
        return CardType.VOCABULARY


class Subject(APIObject):
    """A subject."""

    def __str__(self) -> str:
        return self.object.__str__()

    @property
    def id(self):
        """Get the subject ID."""
        return self.data['id']

    @property
    def object_type(self):
        """Get the object type."""
        return self.data['object']

    @property
    def object(self):
        """Get the object type.

        Returns:
            APIObject: Instance of the APIObject.
        """
        _object = None
        if self.object_type == 'radical':
            _object = Radical(self.data)
        elif self.object_type == 'kanji':
            _object = Kanji(self.data)
        else:
            _object = Vocabulary(self.data)
        return _object


def main():
    """Runs the client."""

    # Work out what commands have been implemented.
    commands = [x for x in dir(Client) if not x.startswith('_')]
    # Make a version of commands that is nice to print.
    command_str = str(commands)[::-1].replace(',', ' or'[::-1], 1)[-2:0:-1]

    cli_description = "A Python client for the Wanikani API."
    # Note that usage is automatically generated.
    parser = ArgumentParser(description=cli_description)

    text = ("The mode in which wanikani-cli will run. Must be " + command_str)
    parser.add_argument("mode", help=text)
    text = ("The API key to use. Defaults to the WANIKANI_API_KEY environment "
            "variable.")
    parser.add_argument("-k", "--api-key",
                        default=os.environ.get('WANIKANI_API_KEY'), help=text)

    # Extract the arguments from the parser.
    args = parser.parse_args()

    # Make sure that we've got an API key and that a mode has been set.
    if args.api_key is None:
        parser.error("api_key is required.")
    if args.mode is None:
        parser.error("A mode must be specified.")

    client = Client(args.api_key)
    res = getattr(client, args.mode)()
    # Do not display command that do not return a response.
    # They already have been displayed.
    if res:
        print(res)


if __name__ == '__main__':
    main()
