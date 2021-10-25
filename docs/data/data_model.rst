.. _data_model:

==========
Data Model
==========

All the fields (variables) to be recorded in the instance's data are defined in the `Data model`_, ``data.models.Data``, a regular `Django model`_ with support for Conversion fields.

Along with the fields, there are configuration options defined in the model about the type and how to use the fields by the classifier and the HTML front-end.

The main distinction between fields is *Classification* and *Metadata*.

Classification fields are those which are used for the Classification service (both at inference and prediction). They are grouped into *Hemogram Fields* and *Auxiliary Fields*.

Metadata fields are those which provide information about the record and are used in other parts of the software.

Classification Fields
=====================

Hemogram Fields
---------------

Are those fields that store the results of a blood measurement or test.

As Hematology equipment may have different outputs (measurement units) according to the country and / or their specification, Data may become not shareable and the Classification service may also become unavailable if there is not a "common denominator" on it.

Addressing this is the definition of *Hemogram Main Fields*, which represent "base unit" variables and will be fed to the Classification service (both at inference and prediction).

For each Hemogram Main Field, *Conversions Fields* may be defined for results in other measurement units. Those values will be converted to the Main Field's unit and stored in the Main Field.

*Hemogram Main Fields* are defined in ``Data.HEMOGRAM_MAIN_FIELDS`` with the measurement unit along the regular Django field definition, i.e.::

    HEMOGRAM_MAIN_FIELDS = {
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

*Conversion Fields* are those which have a ``_U`` in their name and must follow the following naming convention::

    <hemogram_main_field>_U<measurment_unit>[_R<hemogram_main_field>]

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

Conversions are done with the functions defined in `data.conversions`_.

Auxiliary Fields
================

Are those that store auxiliary data to the hemogram results. Auxiliary data is information about the patient that is not a result from a blood measurement and its purpose is to help the classifier achieve better results.

To set a field as Auxiliary, define it in ``Data.AUXILIARY_FIELDS``, i.e.::

    AUXILIARY_FIELDS = [
        'age', 'sex', 'is_at_altitude', 'is_with_other_conds',
    ]

Auxiliary fields will be shown before Hemogram fields in the HTML front-end.

Metadata Fields
===============

Other fields that are not Hemogram nor Auxiliary are considered Metadata.

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


.. _data_model_classifier_configuration:

Classifier Configuration
========================

The constants following constants and methods are used by the internal classifier if it is integrated through ``django-ai`` (see :ref:`internal_classifiers`):

``CHTUID_FIELD``
    Sets which field is used as the instance identifier (used internally).

``LEARNING_FIELDS_CATEGORICAL``
    List of fields used for learning which are `categorical variables`_.

``LEARNING_LABELS``
    Field containing the label to be learnt to predict by the classifier.

``LEARNING_FIELDS_MONOTONIC_CONSTRAINTS``
    `Monotonic Constraints`_ for Learning Fields in the ``field: {-1|0|1}`` format separated by a comma and space, i.e. ``"wbc: -1, rbc: 1``. Ommited fields will use 0. Use "None" to ensure no Monotic Constraints. The constraints will be used if the classifier supports them.

``_get_learning_fields()``
    Returns a list of the fields that will be used by the classifier for learning and prediction.

Those provide a default to the classifiers using the model as data source and can be overridden on a classifier basis in their respective fields, i.e. through the admin interface.

.. _data_model_considerations:

Other Considerations
====================

Hemogram and Auxiliary fields were initially provided as template.

However, :ref:`networking` functionality depends on the Data model.

If the Data model of your network is not syncronized, network classification and data sharing may fail due to unrecongnized fields or validation.

``covid-ht`` is designed to have all the "possible" fields on the Data model and then select which ones you will input through settings according to the output of your local hematology equipment and your blood testing practices.

The fields that are not used (``fields_na``) are not fed to the classifier when performing inference and won't be taken into account if submitted when classifying (this is not the case of missing values in an observation that will be imputed if the classifier does not suppor NA values - see :ref:`internal_classifiers`).

This way, all instances will be able to exchange Data and Classification services, independently of which variables (fields) they effectively recorded.

If you find yourself with the need of adding or altering a field in the Data model, the procedure is:

* Add or modify the Django field
* Add the field to the :ref:`correspondent configuration <data_model_classifier_configuration>` constants if applicable
* Add the field to the :ref:`correspondent setting <settings>` if applicable
* Generate the Django migration (``python manage.py makemigrations``)
* Run the internal test suite (``python manage.py test``)
* Run the migration (``python manage.py migrate``)
* Perform inference in the local classifier if applicable

If the altering is for the original purpose of the project (see :ref:`beyond_covid19`), consider submitting it to the project for inclusion in the project's upstream as the "general" template.


.. _Django model: https://docs.djangoproject.com/en/3.2/topics/db/models/
.. _Data model: https://github.com/math-a3k/covid-ht/blob/master/data/models.py#L105
.. _data.conversions: https://github.com/math-a3k/covid-ht/blob/master/data/conversions.py
.. _categorical variables: https://en.wikipedia.org/wiki/Categorical_variable
.. _Monotonic Constraints: https://scikit-learn.org/stable/auto_examples/ensemble/plot_monotonic_constraints.html