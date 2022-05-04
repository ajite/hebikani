WaniKani CLI
============


This is an alpha release, and it is not working yet.

INSTALL
-------

In a new python environment.

.. code-block:: bash

    python setup.py develop

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

TEST
----

Run the test:

.. code-block:: bash

    python setup.py test

TODO
----

- Submit reviews to the API
- Link cards for the same "subject" together.
