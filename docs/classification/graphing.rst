.. _graphing:

========
Graphing
========

``covid-ht`` graphing support is enabled by the :setting:`GRAPHING` setting.

It generates a graph per pairwise combination of the variables specified in the :setting:`GRAPHING_FIELDS` setting. Note that this variables must be continuos, categorical is not supported. The coordinates of the observation being classified will be plotted on each graph with vertical and horizontal green lines.

Setting :setting:``GRAPHING_DATASET`` to True will plot the dataset used for the classifier training with blue for the NEGATIVE class (not COVID19) and red for the POSITIVE. It aims to provide "context" to the observation.

Using :setting:``GRAPHING_COND_DEC_FUNCTION`` will plot in a contour form the Conditional Decision Function on the variable combination, where darker blue implies more confidence on NEGATIVE and darker red on POSITIVE.

It is conditional because it assumes the rest of the fields to be fixed at the value of the observation, i.e. for an observation ``{rbc: 2, wbc: 2, plt: 100}``, the plot of the Conditional Decision Function on (rbc, wbc) will show how the classifier considers each point of the graph *given* ``plt = 100``, colouring classification regions.

This is not what the classifier outputs, the classifier takes into account all learning fields "at the same time", which, if there are more than 3 is not possible to visualize.

Note that the score (Probability in this case) of the decision is what is to be taken into account, as it takes all the information together, the conditional classification graphic can provide "contradictory" information - i.e. classified as POSITIVE in some variables while NEGATIVE in others.

Taking all the variables / fields together, it is possible to achieve an accurracy above 80% in the Example Dataset, while considering the variables pairwise may lead to contradiction.

The Conditional Decision Function is expensive in computational terms, because of that the :setting:`GRAPHING_MESH_STEPS` can be specified to control the "density" of the mesh in which the function will be evaluated.

Also, techniques which do not support NA values natively and it is not implemented at an engine level have to resort to ``django-ai`` imputation - i.e. SVM - which increases the computational cost.

The implementation can be found ``here <https://github.com/math-a3k/covid-ht/blob/master/base/models.py#L647>``_.
