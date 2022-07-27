"""Handle user input to be converted to hiragana or katakana.
Largely inspired by https://github.com/asweigart/stdiomask

Usage:
    >>> from hebikani.input import input_kana
    >>> input_kana('arigatou')
    'ありがとう'
"""
import re
import sys

import romkan

__all__ = ["input_kana", "KanaWordBuilder"]


def split_at_uppercase(s):
    """Split a string at uppercase letters.

    Args:
        s (str): The string to split.

    Returns:
        List[str]: The list of substrings.

    Examples:
        >>> split_at_uppercase('ITAdaKImasu')
        ['ITA', 'da', 'KI', 'masu']
    """
    for i in range(len(s) - 1)[::-1]:
        if s[i].isupper() and not s[i + 1].isupper():
            s = s[: i + 1] + " " + s[i + 1 :]
        if s[i].isupper() and not s[i - 1].isupper():
            s = s[:i] + " " + s[i:]
    return s.split()


class KanaWordBuilder:
    """Build a kana word."""

    def __init__(self, romaji) -> None:
        self.romaji = romaji

    def add_romaji(self, romaji):
        """Add a romaji character to the kana word.

        Args:
            romaji (str): The romaji character to add.
        """
        self.romaji += romaji

    def remove_last_char(self):
        """Remove the last character from the kana word."""
        last_kana = self.kana[-1]
        if re.match(r"[ぁ-んァ-ン]", last_kana):
            # Check if the last kana is an hiragana or katakana.
            last_kana_romaji = romkan.to_roma(last_kana)
            self.romaji = self.romaji[: -len(last_kana_romaji)]
        else:
            # Remove the last character.
            self.romaji = self.romaji[:-1]

    @property
    def kana(self):
        """Get the kana word. Upper case letters are converted to katakana.
        Lowercase letters are converted to hiragana.
        """
        _kana = []
        for s in split_at_uppercase(self.romaji):
            if s.isupper():
                # Keep the extra romaji in upper case.
                _kana.append(romkan.to_katakana(s).upper())
            else:
                _kana.append(romkan.to_hiragana(s))
        return "".join(_kana)


if sys.platform == "win32":
    from msvcrt import getch  # type: ignore

else:  # macOS and Linux
    import termios
    import tty

    def getch(use_raw_input=True):
        """Get a character from the user.

        Args:
            use_raw_input (bool): Use raw input.

        Returns:
            str: The character.
        """
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            if use_raw_input:
                tty.setraw(sys.stdin.fileno())
            else:
                tty.setcbreak(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch.encode("utf-8")


def input_kana(prompt):
    """Get user input to be converted to hiragana or katakana.

    Raises:
        KeyboardInterrupt: If the user presses Ctrl-C.
    """
    if not isinstance(prompt, str):
        raise TypeError(
            "prompt argument must be a str, not %s" % (type(prompt).__name__)
        )

    kana_word_builder = KanaWordBuilder("")
    sys.stdout.write(prompt)
    sys.stdout.flush()
    while True:
        ch = getch()
        if ch == b"\x03":
            raise KeyboardInterrupt

        key = ord(ch)
        if key == 13 and re.compile(r"^[ぁ-んァ-ン,ー]+$").match(kana_word_builder.kana):
            sys.stdout.write("\n")
            return kana_word_builder.kana
        # Backspace/Del key erases previous output.
        elif key in (8, 127):
            if len(kana_word_builder.kana) > 0:
                # Erases previous character.
                kana_word_builder.remove_last_char()
                sys.stdout.write(f"\r\x1b[K{prompt}{kana_word_builder.kana}")
                sys.stdout.flush()

        elif 0 <= key <= 31:
            sys.stdout.write(f"\r\x1b[K{prompt}{kana_word_builder.kana}\a")
            sys.stdout.flush()
        else:
            # Key is part of the password; display the mask character.
            char = chr(key)
            kana_word_builder.add_romaji(char)
            sys.stdout.write(f"\r{prompt}{kana_word_builder.kana}")
            sys.stdout.flush()
