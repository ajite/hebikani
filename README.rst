WaniKani CLI
============

**This works for review. It is still experimental. Use at your own risk.**

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

TODO
----

- Submit reviews to the API.
- Link cards for the same "subject" together.
- Accept answers with english typos.
- Add more tests.

And more...
