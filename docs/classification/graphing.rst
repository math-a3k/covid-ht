.. _graphing:

========
Graphing
========

``covid-ht`` graphing support is enabled by the :setting:`GRAPHING` setting.

It aims to provide "context" for the classification of an observation.

It generates a graph per pairwise combination of the variables specified in the :setting:`GRAPHING_FIELDS` setting. Note that this variables must be quantitative, categorical variables are not supported at this moment.

The coordinates of the observation being classified will be plotted on each graph with vertical and horizontal green lines.

Setting :setting:`GRAPHING_DATASET` to ``True`` will plot the dataset used for the classifier inference with blue for the ``NEGATIVE`` class (condition not present) and red for the ``POSITIVE``.

Using :setting:`GRAPHING_COND_DEC_FUNCTION` will include in a contour form the *Conditional Decision Function* of the classifier, where darker blue implies more confidence on ``NEGATIVE`` while darker red on ``POSITIVE``.

It is *conditional* because each plane is plotted considering the rest of the fields to be fixed at the value of the observation, i.e. for ``{rbc: 2, wbc: 2, plt: 100}``, the plot of the *Conditional Decision Function* on ``(rbc, wbc)`` will show how the classifier considers each point of the graph *given* ``plt = 100``, while the plot on ``(wbc, plt)`` will be *given* ``rbc = 2``.

These planes aim to provide an approximation to the higher dimensional decision function of the classifier - which is not possible to graph - and should give you the idea of how "is" the observation relative to the classes (``POSITIVE`` / ``NEGATIVE``) in those variables, providing insights about the specifics - i.e. "This patient has these variables in line with the ``POSITIVE`` group yet these others are not, to be considered ``POSITIVE`` it would have had these variables at these values".

**The classifier takes into account all the variables together, its result may consider interactions among them which may not be reflected in the planes**.

**The score** (Probability) of the decision **is what should be taken into account** for reliance, considering the metrics on the general perfomance of the classifier - i.e. accuracy, specificity, sensitivity, etc.

The *Conditional Decision Function* is expensive in computational terms, because of that the :setting:`GRAPHING_MESH_STEPS` can be specified to control the resolution of the mesh in which the function will be evaluated.

Also, techniques which do not support NA values natively and it is not implemented at an engine level have to resort to ``django-ai`` imputation - i.e. SVM - which increases the computational cost.

The implementation can be found `here <https://github.com/math-a3k/covid-ht/blob/master/base/models.py#L656>`_.
