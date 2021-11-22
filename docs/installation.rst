.. _installation:

============
Installation
============

Code repository: https://github.com/math-a3k/covid-ht

Requirements
============

* A working `Python`_ 3.6 or newer (3.9 recommended) installation so you can issue succesfully its version:

.. code-block:: shell

    > python --version

* A working `git`_ installation so you can so you can issue succesfully its version:

.. code-block:: shell

    > git --version

Steps
=====

* Clone the repository:

.. code-block:: shell

    > git clone https://github.com/math-a3k/covid-ht

* Change into the directory, create a virual environment, activate it and install the requirements:

.. code-block:: shell

    > cd covid-ht
    > pythom -m venv .env
    > source .env/bin/activate
    > pip install -r requirements.txt

* Collect the static files and run the test suite:

    > python manage.py collectstatic
    > pythom manage.py test

* Review the :ref:`example_data` settings, set them accordingly, and then run the migrations:

.. code-block:: shell

    > python manage.py migrate

* Create a superuser:

.. code-block:: shell

    > python manage.py createsuperuser

After this, the installation should be complete, you may run the development server for testing it:

.. code-block:: shell

    > python manage.py runserver

Deployment
==========

``covid-ht`` is a Django application with no async features (yet), see this `guide for deployment <https://docs.djangoproject.com/en/3.2/howto/deployment/>`_.

.. _Python: https://www.python.org/
.. _git: https://git-scm.com/