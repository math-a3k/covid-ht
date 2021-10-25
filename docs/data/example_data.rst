.. _example_data:

============
Example Data
============

``covid-ht`` project comes with example data to evaluate the functioning of the different parts of the system and the performance on your hardware.

It is controlled with the :setting:`EXAMPLE_DATA_V2` (enabled by default) and :setting:`EXAMPLE_DATA_SIZE`.

By default, it consists of 1000 observations - 60% positives and 40% negatives (approximately) - with only 15 fields containing data where only 5 fields "discern" the labels:

* 3 differs in 10% in mean only,
* 1 differs in variance only,
* 1 differs in both variance and mean

while the rest are non-informative to the classification problem.

Auxiliary fields also do not provide information.

There is no data contamination - both groups are homogeneous - no outliers, no mixed populations, etc. (see :ref:`robustness`).

With this scenario - COVID19 affects the results in at least 5 variables the same way in a population, bundled classifiers achieve a cross-validated accuracy, precision and recall (sensitivity) above 80% with 1000 observations.

.. note::

	There is **NO WARRANTY** that real data will have the same distribution as the stated. The only way of evaluating the real performance of the test is by using real data.

Further improvements can be obtained by tunning the classifier and / or increasing the sample size.

Example data also allows to evaluate the capacity of your server out-of-the-box to see if it will fulfill your expected demand (see :ref:`load_testing`).

Observations for the example data are generated with `data.utils.get_hemogram_data`_.

.. _managing_example_data:

Managing Example Data
=====================

A ``django-admin`` command, `data.management.commands.example_data`_ is provided to conveniently reset, create and remove the intance's example data.

To safely remove all example data (observations, users and units), use the ``--remove`` option of the ``example_data`` command, i.e.::

	> python manage.py example_data --remove

For resetting example data (discard all observations) use the ``--reset`` option, i.e.::

	> python manage.py example_data --reset

Creating example data (observations, users and units) is done with the ``--create`` option, i.e.::

	> python manage.py example_data --create

For evaluating different scenarios you may use both ``--reset`` and ``--create``, i.e. after editing `data.utils.get_hemogram_data`_, for evaluating with 10000 observations use::

	> COVIDHT_EXAMPLE_DATA_SIZE=10000 python manage.py example_data --reset --create

.. _data.utils.get_hemogram_data: https://github.com/math-a3k/covid-ht/blob/master/data/utils.py#L13
.. _data.management.commands.example_data: https://github.com/math-a3k/covid-ht/blob/master/data/management/commands/example_data.py
