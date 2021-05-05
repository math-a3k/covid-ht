.. _rest_api:

========
REST API
========

The ``covid-ht`` REST API consists mainly of four endpoints:

* ``/classify``
* ``/classify-dataset``
* ``/data``
* ``/data/{uuid}``

This is what allows to:

* integrate with third-party software for:
    * *data inputing*, i.e. hematology equipements, clinical records software, alternative front-ends,
    * *provide classification services*, i.e. clinical records software, alternative front-ends, etc.

* network with other instances to collaborate for providing a better service.

The REST API is namespaced to ``/api/v1``.

It is developed with `django-rest-framework`_, the specification is available in the ``/openapi`` endpoint and the implementation details can be found through `base.v1.views`_ and `data.v1.views`_.

An HTML front-end is available for its endpoints.

.. _rest_api_classify:

Classification REST API Endpoints
=================================

* ``/classify``
* ``/classify-dataset``

Both endpoints provide the information of the classification service via **GET** requests and the service itself via **POST**.

The difference is how the request is done. The first one accepts an observation while the second a list of observations in the ``dataset`` key.

If the ``use_network`` **GET** parameter is set to ``true`` with a **POST** request, it will provide network classification and include the voting information in the response.

.. _rest_api_data:

Data REST API Endpoints
=======================

* ``/data``
* ``/data/{uuid}``

It provides the input and retrieving of data to / from the instance.

The first one (``/data``) provides listing through ``GET`` and creation through ``POST``.

The second one (``/data/{uuid}``) provides retrieve through ``GET`` and update through ``PUT`` and ``PATCH`` (partial).

.. note::

    ``/data`` also provides creation and updating through ``PUT`` and ``PATCH`` which are intended for data sharing between Network Nodes (see :ref:`networking`).

Authentication
==============

Token authentication is supported with the ``Authorization: Token <TOKEN>`` header and session authentication is available in ``/api/auth/login`` and ``/api/auth/logout``.

.. _base.v1.views: https://github.com/math-a3k/covid-ht/blob/master/base/v1/views.py
.. _data.v1.views: https://github.com/math-a3k/covid-ht/blob/master/data/v1/views.py
.. _django-rest-framework: https://django-rest-framework.org