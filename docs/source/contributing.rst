Contributing
============

**WaniKani CLI**  welcomes contributions from the community.

Setting up your own fork of this repo.
--------------------------------------

* On github interface click on Fork button.
* Clone your fork of this repo. ``git clone git@github.com:YOUR_GIT_USERNAME/hebikani.git``
* Enter the directory ``cd hebikani``
* Add upstream repo ``git remote add upstream https://github.com/ajite/hebikani``

Setting up your own virtual environment
---------------------------------------

``poetry install`` already takes care of this for you. You can use ``poetry shell`` to activate it.

Run the tests to ensure everything is working
-----------------------------------------------

Try to write a test for your new feature.

.. code-block:: bash

    poetry run pytest

Format the code
---------------
.. code-block:: bash

    poetry run black

Run the linter
---------------

.. code-block:: bash

    poetry run flake8

Commit your changes
-------------------
This project uses `conventional git commit messages`_.

.. _conventional git commit messages: https://www.conventionalcommits.org/en/v1.0.0/

Example:

.. code-block:: bash

    fix: questions were appearing twice during review session

    Due to a typo issue in the session while loop...
    ......................
    ......................

Push your changes to your fork
------------------------------

Run ``git push origin my_contribution``

Submit a pull request
---------------------

On github interface, click on Pull Request button.

Wait CI to run and one of the developers will review your PR.
