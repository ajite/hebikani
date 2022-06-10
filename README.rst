.. image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/ajite/c90a126b4e926b94c07a36ac78e9a9ad/raw/hebikani_coverage.json
	:target: https://github.com/ajite/hebikani
	:alt: Coverage

.. image:: https://readthedocs.org/projects/hebikani/badge/?version=latest
	:target: https://hebikani.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status

HebiKani
============

**This program is not an official WaniKani client. Use at your own risk.**

A command line interface to do your WaniKani lessons and reviews.

.. raw:: html

  <p align="center">
    <img width="300" height="300" src="https://raw.githubusercontent.com/ajite/hebikani/main/docs/source/_static/logo.png">
  </p>

Story written by OpenAI (text-davinci-002):
   |   The snake had always been interested in learning Japanese, and so when it saw the Crabigator teaching the language, it decided to enroll in the class. The Crabigator was a great teacher, and the snake quickly learned the basics of the language. After a few months, the snake graduated from the class, and as a reward, the Crabigator gave it a magical stone that would allow it to transform into a half-crab, half-snake creature. The snake was thrilled, and immediately used the stone to transform. It then set out to teach Japanese to people all over the world, using its new form to make learning the language fun and easy.

DEMO
----

This is a preview of what a lesson session looks like:

.. figure:: https://raw.githubusercontent.com/ajite/hebikani/main/docs/source/_static/demo.gif
   :alt: CLI demo gif

INSTALL
-------

.. code-block:: bash

    pip install hebikani

If you are missing libraries check the  `documentation <https://hebikani.readthedocs.io/en/latest/install.html>`_

RUN
---

Check the help:

.. code-block:: bash

    hebikani --help

To display your review summary:

.. code-block:: bash

    hebikani summary

To start a review session:

.. code-block:: bash

    hebikani reviews

To start a review session in hard mode with audio and a limited number of reviews:

.. code-block:: bash

    hebikani reviews --hard --autoplay --limit 10

DEVELOPMENT
-----------
This project uses `Poetry <https://python-poetry.org/docs/>`_.

.. code-block:: bash

    poetry install

TEST
----

Run the test:

.. code-block:: bash

    poetry run pytest
