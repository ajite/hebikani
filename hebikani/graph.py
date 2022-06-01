"""All graph related functions
Inspired by:  https://github.com/tammoippen/plotille

Usage:
    >>> from hebikani.graph import hist
    >>> hist([(datetime(2020, 1, 1, 12, 0, 0), 1), (datetime(2020, 1, 2, 15, 0, 0), 2)])
"""
from datetime import datetime
import os

from colorama import Fore


def hist(
    data: list[tuple[datetime, int]],
    width: int = 80,
    total: int = 0,
    linesep: str = os.linesep,
):
    """Create histogram over `data` from left to right

    The values on the left are the dates of this bucket.
    The values on the right are the number of reviews of this bucket.

    Args:
        data: list[tuple[datetime, int]] The items to count over.
        width: int The number of characters for the width (columns).
        total: int The total number of items at the start of the histogram.
        linesep: str The requested line seperator. default: os.linesep

    Returns:
        str: histogram over `data` from left to right.
    """
    canvas = []
    if data:
        # Sort the data by date
        data.sort(key=lambda _data: _data[0])

        # Extract X and Y values
        x_values = [_data[0] for _data in data]
        y_values = [_data[1] for _data in data]

        y_max = max(y_values)
        y_total = total + sum(y_values)

        # Calculate the delimiter width
        delimiter_width = 2 * 8 + len(str(y_total)) + width

        header = "Today | "
        canvas += [
            linesep + header + "{}".format("_" * (delimiter_width - len(header)))
        ]
        lasts = ["", "⠂", "⠆", "⠇", "⡇", "⡗", "⡷", "⡿"]

        current_reviews_nb = total

        for i, x_value in enumerate(x_values):
            x_value_str = x_value.strftime("%I %p")
            current_reviews_nb += y_values[i]
            hight = int(width * 8 * y_values[i] / y_max)
            spaces = " " * (len(str(y_max)) - len(str(y_values[i])))
            canvas += [
                "{} | {}{}{}{} +{}{} | {}".format(
                    x_value_str,
                    Fore.GREEN,
                    "⣿" * (hight // 8) + lasts[hight % 8],
                    Fore.RESET,
                    "⣿" * (width - (hight // 8) + int(hight % 8 == 0)),
                    y_values[i],
                    spaces,
                    current_reviews_nb,
                )
            ]
        canvas += ["‾" * delimiter_width]
    return linesep.join(canvas)
