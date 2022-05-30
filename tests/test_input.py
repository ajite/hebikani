from hebikani.input import KanaWordBuilder


def test_kana_builder():
    """Test the kana builder."""
    assert KanaWordBuilder("a").kana == "あ"
    assert KanaWordBuilder("ohayou").kana == "おはよう"
    assert KanaWordBuilder("BI-dama").kana == "ビーだま"
    assert KanaWordBuilder("SAKKA-").kana == "サッカー"


def test_delete_last_kana():
    """Test deleting the last kana."""
    # remove a single letter kana
    word = KanaWordBuilder("ohayou")
    word.remove_last_char()
    assert word.kana == "おはよ"

    # remove a 2 letters kana
    word = KanaWordBuilder("onna")
    word.remove_last_char()
    assert word.kana == "おん"

    # remove a katakana
    word = KanaWordBuilder("haHA")
    word.remove_last_char()
    assert word.kana == "は"

    # remove a letter
    word = KanaWordBuilder("haH")
    word.remove_last_char()
    assert word.kana == "は"

    # remove special character
    word = KanaWordBuilder("ha-")
    word.remove_last_char()
    assert word.kana == "は"


def test_add_char_to_builder():
    word = KanaWordBuilder("o")
    assert word.kana == "お"

    word.add_romaji("h")

    assert word.kana == "おh"

    word.add_romaji("a")

    assert word.kana == "おは"

    word.add_romaji("YO")

    assert word.kana == "おはヨ"

    word.add_romaji("Yo")

    assert word.kana == "おはヨYお"

    word.add_romaji("hh")

    assert word.kana == "おはヨYおhh"

    word.add_romaji("a")
    assert word.kana == "おはヨYおっは"
