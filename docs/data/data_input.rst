.. _data_input:

==========
Data Input
==========

Each instance define *Units* to organize data input of *Users*.

A Unit is intended to be a source of data for the instance, i.e. clinical laboratories of hospitals or health services' providers, independent laboratories, network nodes, etc.

A User is who inputs data, i.e. Health Workers (clinical laboratories', health records', nurses), hematology equipment, third-pary software, network nodes, etc.

Users are organized into Units with two roles: Manager and Data Inputter. The only differences between roles is that Manager can create and update users.

Each user has access to an HTML interface for inputing the data and the REST API.

To address the posible lag between the results of general and specific testing, a **Unit Internal Identifier** field is provided.

The field should contain an unique identifier to the Patient, i.e. National Identity Number, Social Security Number, Hospital Admission code, etc.

This allows to create and update the data as results arrive from different sources.

Once the specific and general results have been entered, the Unit Internal Identifier should be removed in order to mark the record as *Finished* for anonymizing (see :ref:`data_privacy`) and feeding the Classification service.

The process can be automatic and / or manual.

Automatic
=========

In the cases where the hematology equiment can post its results via HTTP, a REST endpoint is provided for inputting data to the system (see :ref:`rest_api_classify`).

In the cases where the results are stored digitally and accessable, i.e. a RDBMS, the input process can be scripted through the REST enpoints (see :ref:`rest_api_classify`).

Same is for medical records (third party) software.

Manual
======

In the other cases, where printed results are the way of exchanging information, those must be manually entered to the ``covid-ht`` instance in order to use them.

For that case, ``covid-ht`` provides an HTML front-end designed for touch screens - i.e. smart-phones - and numeric keyboards with a mouse to confortably input the data.
