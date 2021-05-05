.. _networking:

==========
Networking
==========

Each instance (or server) of ``covid-ht`` can network with others to share data and improve their classification service.

Under this context, instances are called *Nodes*.

Networking is done through the :ref:`rest_api`. Every service that implements it accordingly can network with the instance.

Each node has an unique identifier, the **CHTUID** (*Covid-HT Unique IDentifier*) - a case-sensitive 5 characters alphanumeric string that will identify the instance in network - set in the :setting:`CHTUID` setting.

Node creation and configuration is done with the admin interface (``/admin/base/networknode``).

Configuration
=============

Besides a unique name, each Node has:

* an internal user (User) and unit (Unit) associated with it for the incoming data from sharing if enabled, and
* an external user (Remote User) with an authentication token (Remote User Token) for sending data to the node if sharing is enabled.

The internal user should have an Authentication Token (generated in the admin interface - ``/admin/authtoken/tokenproxy/``) which should be provided to the node in order to be able to send data.

Data Sharing
------------

If enabled, Data created within the local node will be sent to the external node based on the mode selected:

On Update
	Will send the Data each time a record get created or updated
On Finished
	Will send the Data only when it is marked as "Finished"

Each node will propagate that Data through its network also, this is where the ``CHTUID`` becomes strictly neccesary to identify where the Data was created - Data from a node's unit may not be created by the node but propagated by it.

Classification Service
----------------------

If :ref:`network_voting` is enabled and is enabled for the node, each classification request recieved by the instance will generate another request to the node in order to obtain its vote.

Nodes are also :ref:`external_classifiers`, the same configuration applies.

Other Considerations
====================

Agreggation of statistical estimators (classifiers) make assumptions on the data and the estimators being aggregated. Those assumptions may not hold in the case, so in general, the "votes" may be regarded as "opinions".
