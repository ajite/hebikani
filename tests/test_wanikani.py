import os
from unittest.mock import DEFAULT, patch

from wanikanicli.wanikani import Client, Kanji

from .data import (API_KEY, get_specific_subjects,
                   get_subject_without_utf_entry, get_summary)


@patch('wanikanicli.wanikani.http_get')
def test_summary(mock_http_get):
    """Test the summary."""
    mock_http_get.return_value = get_summary
    client = Client(API_KEY)
    summary = client.summary()
    assert summary.lessons == [25, 26]
    assert summary.reviews == [21, 23, 24]
    assert summary.nb_lessons == 2
    assert summary.nb_reviews == 3


@patch('wanikanicli.wanikani.http_get')
def test_card_creation(mock_http_get):
    """Test the card creation."""
    mock_http_get.return_value = get_specific_subjects
    client = Client(API_KEY)
    subjects = client._subject_per_id([440])
    assert subjects[0].id == 440
    assert subjects[0].object_type == 'kanji'
    assert isinstance(subjects[0].object, Kanji)
    assert subjects[0].object.cards[0].front == '一'
    assert subjects[0].object.cards[0].back == ['one']
    assert subjects[0].object.cards[1].front == '一'
    assert subjects[0].object.cards[1].back == ['いち', 'ひと', 'かず']


@patch('requests.get')
def test_ascii_art(mock_request_get):
    """Check if the ASCII art is correctly displayed."""
    """Test the ascii art creation when no utf character."""

    # 32x32 png image sample from wanikani API
    img_f = open(os.path.join(os.path.dirname(__file__), 'assets/no_utf.png'), 'rb')

    # the image in ascii the desired ASCII format
    ascii_f = open(os.path.join(os.path.dirname(__file__), 'assets/no_utf.txt'), 'r')

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

