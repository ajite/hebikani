from .data import *
from wanikani import Client, Kanji
from unittest.mock import patch


@patch('wanikani.http_get')
def test_summary(mock_http_get):
    """Test the summary."""
    mock_http_get.return_value = get_summary
    client = Client(API_KEY)
    summary = client.summary()
    assert summary.lessons == [25, 26]
    assert summary.reviews == [21, 23, 24]
    assert summary.nb_lessons == 2
    assert summary.nb_reviews == 3

@patch('wanikani.http_get')
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
