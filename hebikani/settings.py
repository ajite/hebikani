import datetime
import json
import os
import sys

# get_settings_path was taken from
# Pyglet <https://github.com/pyglet/pyglet/blob/master/pyglet/resource.py>
# and modified to use sys.platform instead of pyglet.compat_platform


def get_settings_path(name):
    """Get a directory to save user preferences.

    Different platforms have different conventions for where to save user
    preferences, saved games, and settings.  This function implements those
    conventions.  Note that the returned path may not exist: applications
    should use ``os.makedirs`` to construct it if desired.

    On Linux, a directory `name` in the user's configuration directory is
    returned (usually under ``~/.config``).

    On Windows (including under Cygwin) the `name` directory in the user's
    ``Application Settings`` directory is returned.

    On Mac OS X the `name` directory under ``~/Library/Application Support``
    is returned.

    Args:
        name (str): The name of the application.

    Returns:
        str: The path to the application's settings directory.
    """

    if sys.platform in ("cygwin", "win32"):
        if "APPDATA" in os.environ:
            return os.path.join(os.environ["APPDATA"], name)
        else:
            return os.path.expanduser(f"~/{name}")
    elif sys.platform == "darwin":
        return os.path.expanduser(f"~/Library/Application Support/{name}")
    elif sys.platform.startswith("linux"):
        if "XDG_CONFIG_HOME" in os.environ:
            return os.path.join(os.environ["XDG_CONFIG_HOME"], name)
        else:
            return os.path.expanduser(f"~/.config/{name}")
    else:
        return os.path.expanduser(f"~/.{name}")


def save_settings(filename, settings):
    """Save settings to a JSON file.

    Args:
        filename (str): The name of the file to save to.
        settings (dict): The settings to save.
    """
    setting_path = get_settings_path("hebikani")
    if not os.path.exists(setting_path):
        os.makedirs(setting_path)
    filename = os.path.join(setting_path, filename)

    with open(filename, "w") as f:
        json.dump(settings, f, indent=4, sort_keys=True)


def load_settings(filename):
    """Load settings from a JSON file.

    Args:
        filename (str): The name of the file to load from.

    Returns:
        dict: The settings.
    """
    setting_path = get_settings_path("hebikani")
    if not os.path.exists(setting_path):
        os.makedirs(setting_path)
    filename = os.path.join(setting_path, filename)

    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    else:
        return {}


def setting_creation_date(filename) -> datetime.datetime:
    """Get the creation date of the settings file.

    Args:
        filename (str): The name of the file to load from.
    Returns:
        datetime.datetime: The creation date.
    """
    setting_path = get_settings_path("hebikani")
    filename = os.path.join(setting_path, filename)
    if os.path.exists(filename):
        ctime = os.path.getctime(filename=filename)
        return datetime.datetime.fromtimestamp(ctime)
    else:
        return None
