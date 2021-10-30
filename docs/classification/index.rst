==============
Classification
==============

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   internal_classifiers
   external_classifiers
   graphing


One of the main services that ``covid-ht`` provides is the Classification service.

The ``covid-ht`` project encapsulates all the classification logic in the `CurrentClassifier object`_. This object performs the classification at all parts of the instance and can be configured by its admin interface (``/admin/base/currentclassifier``).

Local Classifier
================

Each instance of ``covid-ht`` provides a classification service by itself, the local classifier is the one that provides such.

The local classifier may be internal or external to the instance, independently of it works, it will be the "vote" of the instance in the context of a network or the classification result if stand-alone.

Internal classifiers are those integrated to the ``covid-ht`` instance through the code base while external ones rely on a REST API request for their service.

You may choose either internal or external (external takes preference if defined), only one will be used.

For more information, see :ref:`internal_classifiers` and :ref:`external_classifiers`.

.. _network_voting:

Network Voting
==============

If enabled by **Network Voting Policy**, the Classificatin service will request to other(s) network's node(s) the classification of the data requested to the instance.

The result of the classification by the network's nodes are considered as "votes", which, according to the **Network Voting Policy** and the **Breaking Ties Policy** or **Network Voting Threshold**, will determine the final result of the classification provided by the instance.

The final score (probability in this case) of the classification will be ponderated among the scores of the votes of the same class, i.e. if the classification is ``POSITIVE`` the score will be the average of the scores of the positive votes.

The votes are presented in the HTML front-end automatically, for the REST API see :ref:`rest_api`.

If **Network Voting Policy** is disabled, the local classifier will be used stand-alone.

For more information, see :ref:`networking`.


.. _CurrentClassifier object: https://github.com/math-a3k/covid-ht/blob/master/base/models.py#L89