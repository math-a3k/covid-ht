.. _installation:

============
Installation
============

Code repository: https://github.com/math-a3k/covid-ht

Requirements
============

* A working `Python`_ 3.6 or newer (3.9 recommended) installation so you can issue succesfully its version:

.. code-block:: shell

    > python -V

* A working `git`_ installation so you can clone the repository:

.. code-block:: shell

    > git clone https://github.com/math-a3k/covid-ht


In your computer
================

* Change into the directory, create a virual environment, activate it and install the requirements:

.. code-block:: shell

    > cd covid-ht
    > pythom -m venv .env
    > source .env/bin/activate
    > pip install -r requirements.txt

* Run the migrations the following order:

.. code-block:: shell

    > python manage.py migrate base
    > python manage.py migrate data 0001

* Review the :ref:`example_data` settings, set them accordingly and then run all the pending migrations:

.. code-block:: shell

    > python manage.py migrate

.. note::
  You can safely remove it at any time by issuing ``python manage.py remove_example_data``.

* Create a superuser:

.. code-block:: shell

    > python manage.py createsuperuser

After this, the installation should be complete, you may run the development server for using it:

.. code-block:: shell

    > python manage.py runserver

In a server
===========

``covid-ht`` is a Django application with no async features yet, see this `guide <https://docs.djangoproject.com/en/3.2/howto/deployment/>`_.

.. _Python: https://www.python.org/
.. _git: https://git-scm.com/