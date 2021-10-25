.. _settings:

========
Settings
========

.. contents::
    :local:
    :depth: 1

Here's a list of settings specific to ``covid-ht``, for Django settings reffer `here <https://docs.djangoproject.com/en/3.2/ref/settings/>`_.

.. setting:: DATA_PRIVACY_MODE

``DATA_PRIVACY_MODE``
=====================

Default: ``True``

Enables / Disables the Data Privacy Mode: data is only shown to registered users (see :ref:`data_privacy`).

.. setting:: CHTUID

``CHTUID``
==========

Default: ``cHT00``

Covid-HT Unique IDentifier - a case-sensitive 5 characters alphanumeric string that will identify the instance in network (see :ref:`networking`).

.. setting:: CHTUID_USE_IN_CLASSIFICATION

``CHTUID_USE_IN_CLASSIFICATION``
================================

Default: ``True``

Whether to use the CHTUID as a categorical variable in the Internal Classifier. Switching requires perfoming inference on the classifier (see :ref:`data_model`).

.. setting:: EXAMPLE_DATA

``EXAMPLE_DATA_V2``
===================

Default: ``True``

Whether generate example data on migrations when creating the database and alert the existance in the HTML front-end (see :ref:`example_data`).

``EXAMPLE_DATA_SIZE``
=====================

Default: 1000

Size of the dataset generated in the example data - either by migrations or the ``example_data`` django-admin command (see :ref:`example_data`).

``EXAMPLE_DATA``
================

Default: ``True``

Whether generate example data on migrations (see :ref:`example_data`).

.. warning::
    This setting is deprecated and soon-to-be-removed, use :setting:`EXAMPLE_DATA_V2`.

.. setting:: EXAMPLE_SIZE_COVID19

``EXAMPLE_SIZE_COVID19``
========================

Default: ``600``

Size of COVID19 sample to be generated if :setting:`EXAMPLE_DATA` is enabled (see :ref:`example_data`).

.. warning::
    This setting is deprecated and soon-to-be-removed, use :setting:`EXAMPLE_DATA_SIZE` and edit the proportion in ``get_hemogram_data`` (see :ref:`example_data`).

.. setting:: EXAMPLE_SIZE_NO_COVID19

``EXAMPLE_SIZE_NO_COVID19``
===========================

Default: ``400``

Size of COVID19 sample to be generated if :setting:`EXAMPLE_DATA` is enabled (see :ref:`example_data`).

.. warning::
    This setting is deprecated and soon-to-be-removed, use :setting:`EXAMPLE_DATA_SIZE` and edit the proportion in ``get_hemogram_data`` (see :ref:`example_data`).

.. setting:: HEMOGRAM_MIN_NUM_SUBMIT

``HEMOGRAM_FIELDS_MIN_NUM_SUBMIT``
==================================

Default: ``6``

Minimum number of fields required for the Classification service. (see :ref:`internal_classifiers`).

.. setting:: DATA_INPUT_FORM_FIELDS

``DATA_INPUT_FORM_FIELDS``
==========================

Default: ``[ <list_of_all_fields> ]``

Fields to be used in the data input form in the HTML front-end. Should be adjusted according to the output of your equipment.

.. setting:: DATA_CLASSIFICATION_FORM_FIELD

``DATA_CLASSIFICATION_FORM_FIELDS``
===================================

Default: ``__all__``

Fields to be used in the data classification form in the HTML front-end (home).


``IMAGE_GENERATION``
====================

Default: ``False``

Enable image generation for the classification service (currently only in the HTML front-end).


``IMAGE_GENERATION_FIELDS``
===========================

Default: ``["rbc", "wbc", "hgb", "lymp"]``

Fields to be used in the image generation.

