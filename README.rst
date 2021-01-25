========
covid-ht
========

.. image:: https://travis-ci.com/math-a3k/covid-ht.svg?branch=master
    :target: https://travis-ci.com/math-a3k/covid-ht

covid-ht aims to provide a tool to efficiently build and manage an hemogram classifier and make it effectively available for widespread use in order to improve detection and increase the use efficiency of specific testing of COVID19 cases. See `About <https://covid-ht.herokuapp.com/about>`_.

Installation
============

* Clone the repository:

.. code-block:: shell

    > git clone https://github.com/math-a3k/covid-ht


* Change into the directory, create a virual environment, activate it and install the requirements:

.. code-block:: shell

    > cd covid-ht
    > pythom -m venv .env
    > source .env/bin/activate
    > pip install -r requirements.txt


* Run the migrations the following order:

.. code-block:: shell

    > python manage.py migrate ai_base
    > python manage.py migrate supervised_learning
    > python manage.py migrate base
    > python manage.py migrate data 0001


* Set EXAMPLE_DATA to ``False`` in the project settings if you don't want the example data (and the home message), or review the EXAMPLE_SIZE_COVID19 and EXAMPLE_SIZE_NO_COVID19 settings and then run all the pending migrations:

.. code-block:: shell

    > python manage.py migrate


* Create a superuser:

.. code-block:: shell

    > python manage.py createsuperuser


* Run the server:

.. code-block:: shell

    > python manage.py runsever


Testing
=======

Be sure of collecting static files before running tests:

.. code-block:: shell

    > python manage.py collecstatic


Development
===========

covid-ht currently uses an unreleased branch of django-ai (``covid-ht``). If you wish to modify and/or contribute to this part of the tool, the easiest seems to be cloning the django-ai repository and install the package in "editable mode":

.. code-block:: shell

    > git clone https://github.com/math-a3k/django-ai
    > cd django-ai
    > git checkout -b covid-ht
    > pip install -e /path/to/cloned/django-ai


This way, any changes you make to your local copy of django-ai will be reflected inmediately in your covid-ht's.

See it in action
================

https://covid-ht.herokuapp.com

Communication Channels
======================

* covid-ht@googlegroups.com
* https://github.com/math-a3k/covid-ht

License
=======

covid-ht is distributed under the GNU Lesser General Public License 3 (LGPLv3) or - at your choice - greater.


Made with love for all humans of the world.
