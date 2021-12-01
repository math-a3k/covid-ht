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

The object that performs internally the task is a singleton of ``CurrentClassifier`` [#currentclassifier]_, which can be configured by its admin interface (``/admin/base/currentclassifier``). Setting this will determine the behavior of the instance on the matter.

Classification can be provided in two ways: locally or by networking.

Local classification is referred to the classification provided by the instance itself, as a stand-alone. Each ``covid-ht`` instance encapsulates a lower level classification technique (or algorithm, engine) for which provides an interface.

Network classification is referred to the agreggation of the local classification of the related ``covid-ht`` instances. The instance queries other instances for their classification and the result is a combination of the them. 

Local Classifier
================

Determines what will be used as the classification engine for the instance itself, as a stand-alone.

It will be the "vote" of the instance in the context of a network classification.

The local classifier may be internal or external to the instance.

Internal classifiers are those integrated to the ``covid-ht`` instance through the codebase, while external ones rely on a REST API request to a third-party service, acting as a proxy.

You may choose either internal or external, only one will be used (external takes preference if defined).

For more information, see :ref:`internal_classifiers` and :ref:`external_classifiers`.

.. _network_voting:

Network Voting
==============

Network classification is enabled by setting a **Network Voting Policy**, for which it will request to other(s) network's node(s) the classification of the data requested to the instance.

The result of the classification by the network's nodes are considered as "votes", which, according to the **Network Voting Policy** and the **Breaking Ties Policy** or **Network Voting Threshold**, will determine the final result of the classification provided by the instance.

When deciding by **Majority**, ties can be resolved either by the "opinion" of the local instance, or by the "opinion" with the highest "confidence" (score).

For using a veto policy (**Minimum of Positives** or **Minimum of Negatives**) a **Voting Threshold** must be set, i.e. for a threshold of 3, an observation will be ``POSITIVE`` if three nodes of the network vote that way, or, for the second with a threshold of one, it will be ``NEGATIVE`` if one of the nodes considers it.

The final score (probability in this case) of the classification will be ponderated among the scores of the votes of the same class, i.e. if the classification is ``POSITIVE`` the score will be the average of the scores of the positive votes.

The votes are presented automatically when the service is requested in the HTML front-end, while for the REST API it has to be set in the request (see :ref:`rest_api`).

**Network Voting Policy** (network classification) can be enabled or disabled at any time, the local classifier will be used stand-alone instead.

For more information, see :ref:`networking`.

.. rubric:: Footnotes

.. [#currentclassifier] https://github.com/math-a3k/covid-ht/blob/master/base/models.py#L89
