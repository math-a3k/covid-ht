.. _data_privacy:

============
Data Privacy
============

Privacy is taken into account very seriously: Patient's Data is Patient's Data.

There may be local regulations about Health Records.

The part of the data that identifies the individual that generated the data **is not needed to the purpose of building the classifier**.

Anonymization
=============

The process of removing the parts of the data that identifies the individual that generated the data is called *Anonymization*.

Perfect Anonymization is achieved when is not reasonable to preffer one individual over another as the generator of the data, given of any extra information.

Perfect Anonymization is not achievable due to the domain of the problem.

An Anonymization policy should balance the trade-off between identifiability (privacy) and usefulness of the data.

Although Hemogram results are "highly anonym" (identifying a person by the blood measurements in a certain moment of time is difficult), as a whole it is still a Health Record and should require Patient's consent for making it public as it may have consecuences - i.e. COVID19 status or certain conditions may become sensitive in certain situations - **if the record gets identified**.

The only field that maps the results to a specific person is the **Unit Internal Identifier**.

While the specific testing and blood sampling are assumed to be taken "simultaneously", there may be a lag between the results of both parts due to the type of testing, equipment and operational capacity. This lag may render neccesary to input the results at different moments of time, making neccesary to identify the partial data for updating.

Once the data is completed, the Patient identification information **is not needed to the purpose of building the classifier**.

By design, ``covid-ht`` requires that this field is stripped in order to use the Data as an input for the Classification service.

This field is only shown to Unit's members and not propagated through the network when **Data Sharing Mode** is set to **On Update**.

The other fields that provide information about the specific person are Auxiliary and Metadata fields:

  "An obese person of african ethnicity with diabetis, hepatic failure and cancer, height 182 cm, BMI 43.7, ..., had these blood measurements and tested POSITIVE for COVID19 in Perú [, Lima, [Hospital Lab]] [on 2021-02-01]"

Auxixiliary fields are intended improve the Classification performance, to prescind from them may affect it considerable (see :ref:`internal_classifiers`) and therefore its usefulness.

However, the probability of identifying a specific person in the population that may provide the data to the instance by those fields should be **very low** for most of the individuals.

Therefore, a record is considered to be anoynimized when the **Unit Internal Identifier** is removed.

Once the data has been anonymized, restrictions about Health records should not apply and the data may be publicly available.

Data Privacy Mode
=================

Healthcare units may already have data in their historical records for using the tool and build a classifier, there shouldn't be any legal impediments to use that data internally - as it is used in their management and operation.

There shouldn't be also any impediments of sharing the classifier - or the classifying service - as it can be considered as sharing knowledge, just as experience about therapies and their effectiveness in their operations is usually shared.

However, sharing data may require patients' consent - which may be difficult to get for historical records - or other legal solutions which are exogenous to healthcare units.

For the cases when sharing data (disclosing) is not possible, ``covid-ht`` provides a *Data Privacy Mode* which prevents any data - anonymized or not - to be shown to any not registered within the instance, enabled by the :setting:`DATA_PRIVACY_MODE` setting.

Other Considerations
====================

There is no option in ``covid-ht`` for restricting the Classification service. If you wish to restrict the usage of the whole instance, it should be done by setting up authentication at a web server level.
