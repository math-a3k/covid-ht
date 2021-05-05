.. _load_testing:

Load Testing of covid-ht Instances
==================================

covid-ht includes scripts to estimate the instance capacity and to simulate
usage scenarios in order to fulfill demand.

Those scripts are meant to be run with `locust <https://locust.io>`_ and
located in the ``locustfiles/`` directory.

Installation
------------

* Install the load testing requirements:

.. code-block:: shell

    > (activate your virtualenv)
    > pip install -r requirements_load_testing.txt


Configuration
-------------

If the Example Data is not available, you will have to provide a user and its
credentials by setting the counterintuitively named environment variables
``CHTLT_USER_USERNAME``, ``CHTLT_USER_PASSWORD`` and ``CHTLT_USER_AUTH_TOKEN``.


Estimating Instance Capacity
----------------------------

* Make sure that your instance is running (i.e. already deployed or with
  ``./manage.py runserver``)

* From the base dir of the distribution, run:

.. code-block:: shell

    > locust -f locustfiles/<load_testing_file>.py

Four tests are provided:

* ``api_classify``
	for testing classification via the REST API,
* ``api_data_input``
	for testing data input via the REST API,
* ``classify``
	for testing classification via the HTML front-end,
* ``data_input``
	for testing data input via the HTML front-end.


Each test will stress-test the instance in its particular way, giving an
estimate of the instance capacity to fulfill demand.

Details of the tests are found in their respective files.

Simulating Usage Scenarions
---------------------------

Two different processes are provided for simulating usage scenarios:

* ``doctors``
	simulate doctors attending patients,
* ``inputters``
	simulate data inputters inputting hemogram results.

Details of the processes are found in their respective files.

For running the scenario - with your instance running - from a shell run:

.. code-block:: shell

    > locust -f locustfiles/doctors.py

and from *another* shell:

.. code-block:: shell

    > locust -f locustfiles/inputters.py --web-port 8090

The processes are meant to be ran simultaneously, you can add more processes
simulating the classification requests incoming from the network or other
local sources

Notes
-----

* Classification performance depends on the Current Classifier
  selected for the instance.
* Data input test will generate actual data in your instance.
* `locust Documentation <https://docs.locust.io/en/stable/>`_.
