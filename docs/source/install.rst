Installation
============

Python Version
--------------

We recommend using the latest version of Python. 3.9 and newer.

.. code-block:: bash

    pip install hebikani


**Note**: You will need the dependencies described below to run this program.

Dependencies
------------

OSX
~~~

Please ensure that you have commandline-tools from xcode installed

.. code-block:: bash

    xcode-select --install.

We need it for:

* `pyobjc`_ (required to play audio).

.. _pyobjc: https://pypi.org/project/pyobjc/

Linux
~~~~~

You will need to install manually run:

.. code-block:: bash

    sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0

We need it for:

* `PyGObject`_ (required to play audio).

.. _PyGObject: https://pypi.org/project/pygobject/


Windows
~~~~~~~

.. warning::

    | In the event that the Japanese characters do not display, make sure that you are using a TrueType font that supports Japanese. **SimSun-ExtB** is a good choice.
    |
    | On PowerShell you can change the font by clicking on the icon in the top-left corner of the window and select Properties, then change to the Fonts tab and select **SimSun-ExtB**.


Development
-----------

This project uses `Poetry <https://python-poetry.org/docs/>`_.

.. code-block:: bash

    poetry install
    poetry shell
    hebikani --help
