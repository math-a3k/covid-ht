.. _data_input:

========
Data I/O
========

Each instance define *Units* to organize data input of *Users*.

A Unit is intended to be a source of data for the instance, i.e. clinical laboratories of hospitals or health services' providers, independent laboratories, network nodes, etc.

A User is who inputs data, i.e. Health Workers (clinical laboratories', health records', nurses), clinical laboratory equipment, third-pary software, network nodes, etc.

Users are organized into Units with two roles: Manager and Data Inputter. The only differences between roles is that a Manager can create and update users for the Unit and will be listed as a reference in the HTML front-end.

Each user has access to an HTML interface for inputing the data and the REST API.

To address the posible lag between the results from different sources, a **Unit Internal Identifier** field is provided.

The field should contain an unique identifier to the Patient, i.e. National Identity Number, Social Security Number, Hospital Admission code, etc.

This allows to create and update the data as results arrive at different moments of time.

Once all the information have been entered for the data, the Unit Internal Identifier should be removed in order to mark the record as *Finished* for anonymizing (see :ref:`data_privacy`) and feeding the Classification service.

The process can be automatic and / or manual.

Automatic
=========

A REST endpoint is provided for input / output data from / to the system (see :ref:`rest_api_data`).

This allows to automatize in situations where:

* the clinical equiment (or any third party software) can post its results via HTTP,
* the results are stored digitally and accessable, i.e. a RDBMS (the input process can be scripted through the REST enpoints), or
* consuming data collected in the instance for further processing, i.e. descriptive analysis, etc.

Manual
======

Where printed results are the way of exchanging information or isn't digitally available, ``covid-ht`` provides an HTML front-end designed for touch screens - i.e. smart-phones - and numeric keyboards with a mouse to confortably input the data or retrieve what has been collected so far.

Other Considerations
====================

The CVS output from the HTML front-end may also be scripted::

	import io
	import pandas as pd
	import requests

	host = "http://127.0.0.1:8000"
	url_csv = host + "/data/csv"
	url_json = host + "/api/v1/data?page=no"
	headers = {"Authorization": "Token TheQuickBrownFox..."}

	request_csv = requests.get(url_csv, headers=headers)
	request_json = requests.get(url_json, headers=headers)

	io_content_csv = io.StringIO(request_csv.content.decode("utf-8"))
	io_content_json = io.StringIO(request_json.content.decode("utf-8"))

	# Only data relevant for statistical analysis
	df1 = pd.read_csv(io_content_csv)
	# All data in the instance with non-relevant columns for analysis
	df2 = pd.read_json(io_content_json)

	print(df1)
	print(df2)

	print(df1["rbc"])
	print(df2[df2["is_finished"] == True]["rbc"])
	list(df2[df2["is_finished"] == True]["rbc"]) == list(df1["rbc"])

