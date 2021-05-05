.. _example_data:

============
Example Data
============

``covid-ht`` project comes with example data to evaluate the functioning of the different parts of the system and the performance on your hardware.

It is controlled with the :setting:`EXAMPLE_DATA` (enabled by default) and its relatived ones.

By default, it consists of 1000 hemograms, 600 positives (:setting:`EXAMPLE_DATA_COVID19`) and 400 negatives(:setting:`EXAMPLE_DATA_NO_COVID19`) with only 15 fields containing data where only 5 fields "discern" the labels:

* 3 differs in 10% in mean only,
* 1 differs in variance only,
* 1 differs in both variance and mean

while the rest are non-informative to the classification problem.

Auxiliary fields also do not provide information.

No data contamination - both groups are homogeneous - no outliers, no mixed populations, etc. (see :ref:`robustness`).

With this scenario, bundled classifiers achieve a cross-validated accuracy above 90%.

It also provides a baseline of the accuracy, precision and recall that the service can provide if 1000 observations are gathered with the same characteristics (covid and non-covid hemograms differing in 5 variables the same way).

That baseline may be improved by tunning the classifier.

This also allows to evaluate the capacity of your server out-of-the-box to see if it will fulfill your expected demand (see :ref:`load_testing`).

The example data is generated in `0006_example_data`_ and `0014_example_data_fix`_ migrations of the ``data`` app.

You can safely remove it at any time by issuing ``python manage.py remove_example_data``.

To re-create the example data, re-run the migrations::

	> python manage.py migrate data zero
	> python manage.py migrate data

.. _0006_example_data: https://github.com/math-a3k/covid-ht/blob/master/data/migrations/0006_example_data.py
.. _0014_example_data_fix: https://github.com/math-a3k/covid-ht/blob/master/data/migrations/00014_example_data_fix.py
