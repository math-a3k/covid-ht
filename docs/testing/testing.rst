=======
Testing
=======

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   load_testing

Internal Testing
================

Be sure of collecting static files before running tests:

.. code-block:: shell

    > python manage.py collecstatic

Then run the test suite:

.. code-block:: shell

    > python manage.py test
