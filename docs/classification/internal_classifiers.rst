.. _internal_classifiers:

====================
Internal Classifiers
====================

Internal classifiers are those integrated to the ``covid-ht`` instance through the codebase.

``covid-ht`` comes with bundled classification techniques (classifiers) which should be well suited for the task. Configuration of the classifiers is available through the corresponding admin interface.

The recommended way of incorporating classifiers to ``covid-ht`` is through the ``django-ai`` API.

``django-ai`` not only provides the neccesary glue to handle the request-response cycle on which Django is based but also takes care of the integration with the framework (i.e. using models as a data source, handling forms, dictionaries or objects as input), provides metadata generation and includes batteries for the task (i.e data imputers, transformations, admin functionality, etc.) resulting in Django model objects with a simple API that can be used across any Django application.
	
To integrate a classification technique, use a Django model which is subclass of ``django_ai.models.SupervisedLearningTechnique`` and it will be listed as an option in the Internal Classifier of CurrentClassifer.

``django-ai`` integrates tightly with ``scikit-learn`` [#scikit_learn]_, examples of how to integrate a sklearn classifier can be found in the bundled classifiers [#bundled_classifiers]_.

A non-taxative list of the classifiers provided by ``scikit-learn`` with a visualization of the partitions induced by the technique on different data scenarios can be found `here <https://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html>`_.

The rationale is to subclass them to adapt for the particular needs, as shown in the ``CovidHTMixin`` [#CovidHTMixin]_.

There is no limitation on which implementation should be used, as long as the ``django-ai`` API is implemented, it will work.

If you find inconvenient to use the ``django-ai`` API, you can override the ``get_local_classifier`` method of the ``CurrentClassifier`` object [#CurrentClassifier]_. The method should return an object with the ``is_inferred`` property, a metadata field and a ``predict`` method that should take a list of observations and a boolean for including scores as arguments for returning the predicted class for each observation with the correspondent score, for example::

	import random


	class FlipCoinClassifier:
	    is_inferred = True
	    metadata = {}

	    def predict(self, observations, include_scores=True):
	        result = [True if random.randint(0, 1) else False
	                  for o in observations]
	        scores = [0.5 if include_scores else None
	                  for o in observations]
	        return (result, scores)


	CurrentClassifier.get_local_classifier = lambda x: FlipCoinClassifier()
	CurrentClassifier.clean = None  # Optional

will make the Classification service work.

Other considerations
====================

There are three important properties that classifier should have:

Non-Available (NA) Support
--------------------------

There are several sources of Non-Available fields, some of them are:

* Different clinical testing practices according to according to circumstances and / or places
* Different capabilities among clinical equipments
* Circumstancial Errors

If the classification technique does not support data with NA fields, an observation with one missing field of the expected is not classifiable.

It will also make sharing data and classification services (and hence networking) highly unlikely (see :ref:`Data model considerations <data_model_considerations>`).

Many techniques does not support NA values natively, having to resort to data imputting.

``django-ai`` provides data imputers for integrating those techniques without loosing functionality.

Data imputation have the caveat that may affect the classification results unadvertly. ``django-ai`` provides an *Introspection imputer* [#Introspection_imputer]_ that uses the same assumptions of the classifier for the case.

Imputting can also be incorporated within the classifier if the engine supports it.

Categorical Data Support
------------------------

Although most of the categorical data [#Categorical_data]_ may be in auxiliary fields (see :ref:`data_model`), clinical tests may be also provide the kind.

Auxiliary data "helps" the classifier to discern shifts in values which are not caused by the presence of a condition.

For example, in the case of hematology, people with african ethnicity have lower RBC than non-african while healthy, people with leukymia have different WBC values, people living at high-altitude have lower oxygen saturation and higher hemoglobin, people at different age have different healthy values, etc.

If there is no auxiliary data, those observations may be "contradictory" to the classifier, leading to poor generalization and poor perfomance.

Many techiques does not support categorical values natively, having to resort to data transformations to take them into account.

``django-ai`` provides a *Categorical Indicator Function Transformation* [#CIFT]_ for integrating those techniques.

Data transformations can also be incorporated within the classifier if the engine supports it, as shown in the ``DecisionTree`` model [#DecisionTree_model]_.

.. _robustness:

Outlier Support
---------------

Many techniques assume that all the data comes from the same population (or process). Auxilliary variables are for discerning sub-populations, but not all sub-populations will be able to be encoded in those.

As the dataset size grows, there will be sub-populations not encoded that will be mixed with others, likely altering the classification boundaries for them and affecting performance (accuracy, precision, recall, etc.) - i.e. in hematology, without the ``age`` auxiliary variable, newborns' hemograms will be "mixed" with adults'.

This scenario is sometimes regarded as "data contamination".

"Outlier" is the technical term for "atypical" in the sense that it does not have "similar characteristics" **relative** to the "most" of the population considered.

There are three main sources of outliers:

* Mixed populations
* "Just different" members of the same population
* Errors in the data input process

Given that:

* It is not feasible to encode all sub-populations in auxiliary variables (it's either impractical or impossible due to not knowning the existance)
* Populations have "just different" members
* It is not feasible to prevent all errors in the data input process

There will be outliers at some point in the dataset.

Techniques that take into account outliers are called "robust", as "contamination" with "outliers" does not affect the conclusions.

If the technique is not robust, the effect of outliers can be mitigated in the preprocess data stage with the caveat that the outlier definition may not be in line with the technique and thus affecting its results unadvertly.

``django-ai`` currently does not provides outlier mitigation functionality, it has to be supported by the technique or incorporated through the engine.


.. rubric:: Footnotes

.. [#scikit_learn] https://scikit-learn.org/stable/
.. [#bundled_classifiers] https://github.com/math-a3k/django-ai/tree/covid-ht/django_ai/supervised_learning
.. [#CurrentClassifier] https://github.com/math-a3k/covid-ht/blob/master/base/models.py#L89
.. [#CovidHTMixin] https://github.com/math-a3k/covid-ht/blob/master/base/models.py#L605
.. [#Introspection_imputer] https://github.com/math-a3k/django-ai/blob/covid-ht/django_ai/supervised_learning/models/data_imputers/introspection_imputer.py
.. [#Categorical_data] https://en.wikipedia.org/wiki/Categorical_variable
.. [#CIFT] https://github.com/math-a3k/django-ai/blob/covid-ht/django_ai/ai_base/models/learning_technique.py#L371
.. [#DecisionTree_model] https://github.com/math-a3k/covid-ht/blob/master/base/models.py#L796
