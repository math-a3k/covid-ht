.. _graphing:

========
Graphing
========

``covid-ht`` graphing support is enabled by the :setting:`GRAPHING` setting.

It generates a graph per pairwise combination of the variables specified in the :setting:`GRAPHING_FIELDS` setting. Note that this variables must be continuos, categorical variables are not supported at this moment. The coordinates of the observation being classified will be plotted on each graph with vertical and horizontal green lines.

Setting :setting:`GRAPHING_DATASET` to ``True`` will plot the dataset used for the classifier inference with blue for the ``NEGATIVE`` class (not COVID19) and red for the ``POSITIVE``. It aims to provide "context" to the observation.

Using :setting:`GRAPHING_COND_DEC_FUNCTION` will plot in a contour form the *Conditional Decision Function* on the variable combination, where darker blue implies more confidence on ``NEGATIVE`` and darker red on ``POSITIVE``.

It is conditional because it assumes the rest of the fields to be fixed at the value of the observation, i.e. for an observation ``{rbc: 2, wbc: 2, plt: 100}``, the plot of the *Conditional Decision Function* on ``(rbc, wbc)`` will show how the classifier considers each point of the graph *given* ``plt = 100``, colouring classification regions on that plane.

These planes - i.e. ``(rbc, wbc)`` - should give you the idea of how "is" the observation relative to the classes (``COVID`` / ``NO-COVID`` in this case) in those variables. **The classifier takes into account all the variables together, its result may consider interactions among them which may not be reflected in the planes**.

**The score** (Probability) of the decision **is what should be taken into account**, considering the metrics on the general perfomance of the classifier in the context - i.e. accuracy, specificity, sensitivity, etc.

There are some caveats on the *Conditional Decision Function*, it is currently provided as a technology preview.

Having this in mind, this could provide insights about specifics of the observation - i.e. "This patient has these variables in line with the ``COVID`` group yet these others are not".

The *Conditional Decision Function* is expensive in computational terms, because of that the :setting:`GRAPHING_MESH_STEPS` can be specified to control the "density" of the mesh in which the function will be evaluated.

Also, techniques which do not support NA values natively and it is not implemented at an engine level have to resort to ``django-ai`` imputation - i.e. SVM - which increases the computational cost.

The implementation can be found `here <https://github.com/math-a3k/covid-ht/blob/master/base/models.py#L656>`_.
