Development
===========

``covid-ht`` currently uses an unreleased branch of ``django-ai`` (``covid-ht``). If you wish to modify and / or contribute to this part of the tool, the easiest seems to be cloning the ``django-ai`` repository and install the package in "editable mode":

.. code-block:: shell

    > git clone https://github.com/math-a3k/django-ai
    > cd django-ai
    > git checkout -b covid-ht
    > pip install -e /path/to/cloned/django-ai

This way, any changes you make to your local copy of ``django-ai`` will be reflected inmediately in your ``covid-ht``'s.
