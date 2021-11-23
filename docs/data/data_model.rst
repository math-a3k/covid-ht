.. _data_model:

==========
Data Model
==========

All the fields (variables) to be recorded in the instance's data are defined in the *Data model* [#data_model_source]_, ``data.models.Data``, a regular *Django model* [#django_model]_ with support for *Conversion fields* [#conversion_fields]_.

Fields are grouped into *Metadata*, *Learning* and *Conversions*.

An extra field is the *Learning Label Field*.

Along with the fields, there are configuration options defined in the model about the type and how to use the fields by classifiers in the Classification Service and the HTML front-end.

The ``covid-ht`` project was developed initially for building a machine-learning test for COVID19 through Hematology, and hence, the template of Data Model provided.

Metadata Fields
===============

Metadata fields are those which provide information about the record and are used for "administrative" aspects of the software, i.e. organizing data input and sharing.

``chtuid``
    Covid-HT Unique Identifier: Provides which ``covid-ht`` instance generated the record

``unit``
    Instance's Unit: Provides which Unit of the instance generated the record

``user``
    User: Provides which User of the instance created or last-updated the record

``is_finished``
    Is Finished: Indicates if the data input process has been finished

``unit_ii``
    Unit Internal Identifier: Maps the Data record to the Physical Person from whom the Data was generated

``uuid``
    Universal Unique IDentifier: Provides an unique identifier of the record among ``covid-ht`` instances

``timestamp``
    Timestamp: Provides the creation or last-updated timestamp of the record

``chtuid`` may be used in the Classification service according to the ``CHTUID_USE_IN_CLASSIFICATION`` setting.


Learning Fields
===============

Learning fields are those which are used for the Classification service (both at inference and prediction). They are grouped into *Auxiliary Fields* and *Main Fields*.

Auxiliary Fields
----------------

Are those which store data which is not a result of a clinical measurement and sometimes it may be obtained prior to sampling. Its purpose is to help the classifier achieve better results with the clinical measurements.

To set a field as Auxiliary, define it in ``Data.AUXILIARY_FIELDS``, i.e.::

    AUXILIARY_FIELDS = [
        'age', 'sex', 'is_at_altitude', 'is_with_other_conds',
    ]

Auxiliary fields will be shown before Main fields in the HTML front-end.

Main Fields
-----------

Are those fields which store a result of a clinical measurement.

As clinical equipment may have different outputs (measurement units) according to the country and / or their specification, Data may become not shareable and the Classification service may also become unavailable if there is not a "common denominator" on it.

Addressing this is the definition of *Main Fields*, which represent "base unit" variables that will be fed to the Classification service (both at inference and prediction).

*Main Fields* are defined in ``Data.MAIN_FIELDS`` with the measurement unit along the regular Django field definition, i.e.::

    MAIN_FIELDS = {
        'rbc': {'unit': 'x1012L', },
        'wbc': {'unit': 'x109L', },
        'mchc': {'unit': 'gL', },
        'lymp': {'unit': 'x109L'},
    }
    ...
    wbc = models.DecimalField(
        _("WBC (x10^9/L)"),
        max_digits=5, decimal_places=3,
        blank=True, null=True,
        help_text=_(
            'White Blood Cells (x10^9/L or x10^3/mm^3 or x10^3/uL^3)'
        ),
        validators=[MinValueValidator(1.0), MaxValueValidator(50.0)]
    )
    mchc = models.SmallIntegerField(
        _("MCHC (g/L)"),
        blank=True, null=True,
        help_text=_('Mean Corpuscular Hemoglobin Concentration (g/L)'),
        validators=[MinValueValidator(2), MaxValueValidator(5)]
    )
    lymp = models.DecimalField(
        _("LYMPH (x10^9/L)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Lymphocytes (x10^9/L)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(30.0)]
    )

Conversion Fields
=================

Addresing the heterogenous units case, for each Main Field, *Conversions Fields* may be defined for results in other measurement units. Those values will be converted to the Main Field's unit and stored in the Main Field besides the original unit.

Conversion Fields are those which have a ``_U`` in their name and must follow the following naming convention::

    <main_field>_U<measurment_unit>[_R<main_field>]

where ``_R`` is optional and reffers to "Relative to Main Field" for addressing percentages-like results, i.e.::

    mchc_UgdL = models.SmallIntegerField(
        _("MCHC (g/dL)"),
        blank=True, null=True,
        help_text=_('Mean Corpuscular Hemoglobin Concentration (g/dL)'),
        validators=[MinValueValidator(20), MaxValueValidator(50)]
    )
    mchc_UmmolL = models.SmallIntegerField(
        _("MCHC (mmol/L)"),
        blank=True, null=True,
        help_text=_('Mean Corpuscular Hemoglobin Concentration (mmol/L)'),
        validators=[MinValueValidator(2), MaxValueValidator(8)]
    )
    lymp_Upercentage_Rwbc = models.DecimalField(
        _("LYMPH (% WBC)"),
        max_digits=4, decimal_places=2,
        blank=True, null=True,
        help_text=_('Lymphocytes (% of White Blood Cells)'),
        validators=[MinValueValidator(0.01), MaxValueValidator(99.0)]
    )

The Conversion Field ``lymph_Upercentage_Rwbc`` will convert its value as the percentage of ``wbc`` and store it in ``lymph`` once the record is saved or the convertion is triggered (if ``wbc`` is 3, and ``lymph_Upercentage_Rwbc`` is 10, ``lymph`` will be 0.3). The fields ``mchc_UgdL`` and ``mchc_UmmolL`` will convert their respective value to g/L and store it ``mchc``.

Conversions are done with the functions defined in ``data.conversions`` [#data_conversions]_. Every Conversion Field should have a unit conversion function to the main unit defined there.

Conversion Fields are not fed into the classification service.

Learning Label Field
====================

The *Learning Label Field* is the one which contains the presence or absense of the condition which its prediction is meant to be learnt from the Auxiliary and Main fields. It may also be reffered as ``LEARNING_TARGET``.

It should be a Boolean field, as currently ``covid-ht`` supports binary classification only.

The label is defined in ``Data.LEARNING_LABELS`` along the regular Django field.

.. note::
    The Auxiliary and Main fields along with the Label is what the Classification Service regards as an *observation*.

.. _data_model_classifier_configuration:

Classifier Configuration
========================

The following constants and methods are used additionally to provide a default to the internal classifiers if they are integrated through ``django-ai`` (see :ref:`internal_classifiers`):

``LEARNING_FIELDS_CATEGORICAL``
    List of fields used for learning which are categorical variables [#categorical_variables]_.

``LEARNING_FIELDS_MONOTONIC_CONSTRAINTS``
    Monotonic Constraints [#monotonic_constraints]_ for Learning Fields in the ``field: {-1|0|1}`` format separated by a comma and space, i.e. ``"wbc: -1, rbc: 1``. Ommited fields will use 0. Use "None" to ensure no Monotic Constraints. The constraints will be used if the classifier supports them.

``_get_learning_fields()``
    Returns a list of the fields that will be used by the classifier for learning and prediction.

Those defaults can be overridden on a classifier basis in their respective fields, i.e. through the admin interface.

Additional Configuration
========================

Other options not otherwise specified:

``CHTUID_FIELD``
    Sets which field is used as the instance identifier (Metadata).

Customizing the Data Model
==========================

For adapting the Data model to your needs, the procedure is:  

* Add, modify or delete the Django field(s)
* Reflect the changes in the :ref:`correspondent configuration <data_model_classifier_configuration>` constants if applicable
* Reflect the changes in the :ref:`correspondent setting <settings>` if applicable
* Generate the Django migration (``python manage.py makemigrations``)
* Run the internal test suite (``python manage.py test``)
* Run the migration (``python manage.py migrate``)
* Perform inference in the local classifier if applicable
* Notify other network nodes if applicable

If the altering is in line with the original purpose of the project, consider submitting it to the project for inclusion in the project's upstream as the "general" template.

.. _data_model_considerations:

Other Considerations
====================

:ref:`networking` functionality (Collaboration) depends on the Data model.

If the Data model of your network is not syncronized, network classification and data sharing may fail due to unrecongnized fields or validation.

``covid-ht`` is designed to have all the "possible" fields on the Data model and then select which ones you will manually input through settings according to the output of your local equipment and your measurement practices.

The fields that are not used (not submitted at all, ``fields_na``) are not fed to the classifier when performing inference and won't be taken into account if submitted when classifying (this is not the case of missing values in an observation that will be imputed if the classifier does not suppor NA values - see :ref:`internal_classifiers`).

This way, all instances the network will be able to exchange Data and Classification services, independently of which variables (fields) they effectively recorded in each one.

If you find yourself with the need of adding or altering a field in the Data model, be sure to notify other instances of your network. Differences in the Data model are shown in Network Node admin.


.. rubric:: Footnotes

.. [#data_model_source] https://github.com/math-a3k/covid-ht/blob/master/data/models.py
.. [#django_model] https://docs.djangoproject.com/en/3.2/topics/db/models/
.. [#conversion_fields] https://github.com/math-a3k/covid-ht/blob/master/data/mixins.py
.. [#data_conversions] https://github.com/math-a3k/covid-ht/blob/master/data/conversions.py
.. [#categorical_variables] https://en.wikipedia.org/wiki/Categorical_variable
.. [#monotonic_constraints] https://scikit-learn.org/stable/auto_examples/ensemble/plot_monotonic_constraints.html
