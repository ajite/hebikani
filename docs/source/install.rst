Installation
============

Python Version
--------------

We recommend using the latest version of Python. 3.9 and newer.
This program does not support windows system.

.. code-block:: bash

    pip install wanikani-cli

**Note**: You will need the dependencies described below to run this program.


Dependencies
------------

OSX
~~~

Please ensure that you have commandline-tools from xcode installed

.. code-block:: bash

    xcode-select --install.

We need it for:

* `pyobjc`_ is required to play audio.

.. _pyobjc: https://pypi.org/project/pyobjc/

Linux
~~~~~

You will need to install manually run:

.. code-block:: bash

    sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0

We need it for:

* `PyGObject`_ is required to play audio.

.. _PyGObject: https://pypi.org/project/pygobject/


Development
-----------

This project uses `Poetry <https://python-poetry.org/docs/>`_.

.. code-block:: bash

    poetry install
    poetry shell
    wanikani-cli --help

If you do not want to use poetry you can use the `requirements.txt` file.

**Note**: External python libraries will need to be added through poetry. Once added we need to generate a new requirements.txt via:

.. code-block::

    poetry export --without-hashes --format requirements.txt --output requirements.txt
