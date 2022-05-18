.. image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ajite/c90a126b4e926b94c07a36ac78e9a9ad/raw/wanikani_cli_coverage.json
	:target: https://github.com/ajite/wanikani-cli
	:alt: Coverage

WaniKani CLI
============

**This program is not an official WaniKani client. Use at your own risk.**

A command line interface to do your WaniKani lessons and reviews.

INSTALL
-------

.. code-block:: bash

    pip install wanikani-cli


RUN
---

Check the help:

.. code-block:: bash

    wanikani-cli --help

To display your review summary:

.. code-block:: bash

    wanikani-cli summary

To start a review session:

.. code-block:: bash

    wanikani-cli reviews

To start a review session in hard mode with audio and a limited number of reviews:

.. code-block:: bash

    wanikani-cli reviews --hard --autoplay --limit 10

DEVELOPMENT
-----------
This project uses `Poetry <https://python-poetry.org/docs/>`_.

.. code-block:: bash

    poetry install

You can also use the generated `requirements.txt` file.

.. code-block:: bash

    pip install -r requirements.txt

Please run that command after adding external libaries through poetry:

.. code-block:: bash

    poetry export --without-hashes --format requirements.txt --output requirements.txt

TEST
----

Run the test:

.. code-block:: bash

    poetry run pytest
