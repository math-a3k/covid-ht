.. _example_data:

============
Example Data
============

``covid-ht`` project comes with example data to evaluate the functioning of the different parts of the system and the performance on your hardware.

It is controlled with the :setting:`EXAMPLE_DATA_V2` (enabled by default) and :setting:`EXAMPLE_DATA_SIZE`.

By default, it consists of 1000 observations - 60% positives and 40% negatives (approximately) - with only 15 fields containing data where only 5 statistically-independent fields "discern" the labels:

* 3 differs in 10% in mean only,
* 1 differs in variance only,
* 1 differs in both variance and mean

while the rest are non-informative to the classification problem.

Auxiliary fields also do not provide information.

There is no data contamination - both groups are homogeneous - no outliers, no mixed populations, etc. (see :ref:`robustness`).

With this scenario - the condition (``COVID19``) affects the results in at least 5 variables the same way in a population, bundled classifiers achieve a cross-validated accuracy, precision and recall (sensitivity) above 80% with 1000 observations.

.. note::

	There is **NO WARRANTY** that real data will have the same distribution as the stated. The only way of evaluating the real performance of the test is by using real data. Its purpose is to demonstrate how negligible impacts or complex patterns to the human eye can be captured by the techniques, or in the other direction, impacts captured by the human eye can be outperformed, and hence, its usefulness as a tool.

Further improvements can be obtained by tunning the classifier and / or increasing the sample size.

Example data also allows to evaluate the capacity of your server out-of-the-box to see if it will fulfill your expected demand (see :ref:`load_testing`).

Observations for the example data are generated with ``data.utils.get_simulated_data`` [#get_simulated_data]_.

.. _managing_example_data:

Managing Example Data
=====================

A ``django-admin`` command, ``example_data`` [#example_data_command]_, is provided to conveniently reset, create and remove the intance's example data.

To safely remove all example data (observations, users and units), use the ``--remove`` option, i.e.::

	> python manage.py example_data --remove

For resetting example data (discard all observations) use the ``--reset`` option, i.e.::

	> python manage.py example_data --reset

Creating example data (observations, users and units) is done with the ``--create`` option, i.e.::

	> python manage.py example_data --create

For evaluating different scenarios you may use both ``--reset`` and ``--create``, i.e. after editing data.utils.get_simulated_data , for evaluating with 10000 observations use::

	> COVIDHT_EXAMPLE_DATA_SIZE=10000 python manage.py example_data --reset --create

Other Considerations
====================

Statistically independent fields (variables) is not a realistic scenario for the effects of a condition, it is more likely to have dependency among variables which may "highlight the pattern to the classifier".

Consider defining in ``get_simulated_data`` [#get_simulated_data]_ the following instead::
	
	data["neut"] = round(data["lymp"] + trunc_normal(0.2, 2, 1, 1, 1)[0]
                         if is_covid19 else
                         trunc_normal(0.1, 30, 8, 4, 1)[0], 2)

and after, in a console issue::
	
	python manage.py example_data --reset --create

then perform inference in the classifier's admin to compare results and classify an observation with the HTML front-end to visualize the new pattern.

Homogeneous groups is also not realistic (see :ref:`robustness`), the only way of generating a realistic example is by collecting real data about the condition.

.. rubric:: Footnotes

.. [#get_simulated_data] https://github.com/math-a3k/covid-ht/blob/master/data/utils.py#L13
.. [#example_data_command] https://github.com/math-a3k/covid-ht/blob/master/data/management/commands/example_data.py
