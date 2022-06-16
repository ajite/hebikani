import hebikani.input as input_kana


def test_kana_builder():
    """Test the kana builder."""
    assert input_kana.KanaWordBuilder("a").kana == "あ"
    assert input_kana.KanaWordBuilder("ohayou").kana == "おはよう"
    assert input_kana.KanaWordBuilder("BI-dama").kana == "ビーだま"
    assert input_kana.KanaWordBuilder("SAKKA-").kana == "サッカー"


def test_delete_last_kana():
    """Test deleting the last kana."""
    # remove a single letter kana
    word = input_kana.KanaWordBuilder("ohayou")
    word.remove_last_char()
    assert word.kana == "おはよ"

    # remove a 2 letters kana
    word = input_kana.KanaWordBuilder("onna")
    word.remove_last_char()
    assert word.kana == "おん"

    # remove a katakana
    word = input_kana.KanaWordBuilder("haHA")
    word.remove_last_char()
    assert word.kana == "は"

    # remove a letter
    word = input_kana.KanaWordBuilder("haH")
    word.remove_last_char()
    assert word.kana == "は"

    # remove special character
    word = input_kana.KanaWordBuilder("ha-")
    word.remove_last_char()
    assert word.kana == "は"


def test_add_char_to_builder():
    word = input_kana.KanaWordBuilder("o")
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
