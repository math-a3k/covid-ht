.. _about:

==================
About ``covid-ht``
==================

``covid-ht`` aims to provide a tool for implementing an AI layer on clinical classification effectively in order to improve detection, information availability and resource efficiency in medical environments.

It provides the IT infrastructure for:

- Data collection
- Classification
- Collaboration

Designed with the loosely coupled principle and the lowest common denominator in mind, from a single individual with a smart-phone scaling up to hundreds easily.

There are three main scenarios that ``covid-ht`` tries to address:

- The particularization of a previously established classification criteria to a specific case and population
- Evidence gathering for supporting heuristics 
- Augmented information from currently-taken measurements

Motivated by helping with the struggle against the COVID19's pandemic in resource-constrainted places where specific testing wasn't available at sufficient quantities (see :ref:`history`) and triggered by watching a Doctor in El Salvador explaining the classification criteria particular to a COVID19 infection of blood measurements [#barrientos]_, and hence the name (``covid-hemogram-test``) and the data template provided.

There is no restriction on any particular condition or hematology only: any diagnostic procedure which includes classification according to numeric real-valued measurements or encoded categories, i.e. results from a clinical laboratory, can benefit from it.

The only requirement is that effects of the conditions on the measurements are consistant to some degree.

`This tool is totally transparent <https://github.com/math-a3k/covid-ht>`_ - built on Free and Open Source Software, Open Standards and distributed under the GNU LGPLv3 license. You may audit it entirely to fully understand how it works, what it provides and its limitations.

Is something not working correctly? Could something be done better? Any questions? Everybody is welcome to join the community for building and using it:

* covid-ht+subscribe@googlegroups.com
* https://github.com/math-a3k/covid-ht


.. _history:

History
=======

Blood Measurement (*hemogram*) is a common practice among Health Professionals as part of the toolkit to diagnose and evaluate a wide variety of health conditions.

While some of the measurements can characterize certain conditions, others provide information about "general functioning" which may reflect the ongoing of conditions.

Diagnosis and evaluation of conditions which take into account hemograms is done by Health Professionals based on individual knowledge and experience.

While there are specific blood measurements for COVID19, those haven't been widely available in many places - i.e. Perú - having to resort to other tools for the diagnosis, i.e. x-rays, tomographies, non-specific Blood Measurements, etc.

Non-specific Blood Measurements - i.e. Complete Blood Counts - are widely available, affordable and already incorporated into the Health Professional practice.

A "general guide" is commonly provided in the results with reference values in order to help "classify" the patient (i.e. healthy or non-healthy).

Departure from those reference values may indicate an ongoing condition - i.e. bacterial or viral infection - which, with the assement of symptoms (and perhaps other diagnosis tools) leads to the diagnosis and therefore treatment.

While there are guidelines to detect an infection through hemogram results, the specific effects on hemograms of COVID19 are being studied, i.e. in `C-reactive protein`_ and `viscosity`_.

*Independently of the causes of such effects, as long as those are consistent to a "considerable" part of the population, a classifier can be developed in order to improve the diagnosing toolkit of Health Professionals.*

This project aims to provide a tool to efficiently build and manage that classifier and make it effectively available for widespread use in order to improve detection, evaluation and resource efficiency of the COVID19 pandemic.

Early detection is deemed to be the greatest success factor in COVID19 treatments.

Improvements in early detection should increase successful treatments, potentially saving lives.

Improved evaluation and resource efficiency can also be achieved with the tool, i.e. by only using expensive specific COVID19 testing - i.e. PCR testing - for assesing full recovery when the classification of the hemogram indicates so.

`A machine-learning classifier can outperform top-level Human experts' classification`_. AI classifiers takes into account relations and differences that are hard to spot to most Humans systematically.

If this classifier achieves an adequate accuracy through hemograms and is made publicly available, all Health Professionals with a smart-phone and Internet access could classify any hemogram with the same accuracy as top-level experts on the matter, improving the information available from the measurement for the case with little to no infrastructure modifications.

.. _C-reactive protein: https://onlinelibrary.wiley.com/doi/10.1111/bjh.17306
.. _viscosity: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8010604/
.. _A machine-learning classifier can outperform top-level Human experts' classification: https://www.theguardian.com/society/2020/jan/01/ai-system-outperforms-experts-in-spotting-breast-cancer


.. rubric:: Footnotes

.. [#barrientos] https://youtu.be/ZO6EaAz465Y?t=570
