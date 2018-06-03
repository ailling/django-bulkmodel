Signals API Reference
=========================

API reference for additional signals included in Django-bulkmodel

-----


Bulk create signals
------------------------

pre_bulk_create
~~~~~~~~~~~~~~~~~~~~

Fired before bulk_create writes data to the database

Parameters:

    - ``instances``: a list of model instances about to be written to the database



post_bulk_create
~~~~~~~~~~~~~~~~~~

Fired after bulk_create has written data to the database

Parameters:

    - ``instances``: a list of model instances that have been written to the database
    - ``queryset``: a queryset of records saved in the bulk create; only applies if ``return_queryset=True`` is passed to ``bulk_create()``


Fired after a bulk-create is issued


-----


Update signals
------------------------


pre_update
~~~~~~~~~~~~

Fired just before ``update()`` performs a homogeneous update

Parameters:

    - ``instances``: a list of instances about to be updated


post_update
~~~~~~~~~~~~

Fired just after ``update()`` performs a homogeneous update

Parameters:

    - ``instances``: a list of instances that have been updated


pre_update_fields
~~~~~~~~~~~~~~~~~~~~~~~~

Fired just before ``update_fields()`` performs a hetergenous update

Parameters:

    - ``instances``: a list of instances about to be updated
    - ``field_names``: a list of fieldnames being updated; if empty, all fields are being updated
    - ``field_defaults``: defaults for each field, provided as a dictionary
    - ``batch_size``: the batch size used for the update



post_update_fields
~~~~~~~~~~~~~~~~~~~~~~~~

Fired just after ``update_fields()`` performs a heterogeneous update

Parameters:

    - ``instances``: a list of instances about to be updated
    - ``queryset``: a queryset of records updated, if ``return_queryset=True`` is passed to update_fields
    - ``field_names``: a list of fieldnames being updated; if empty, all fields are being updated
    - ``field_defaults``: defaults for each field, provided as a dictionary
    - ``batch_size``: the batch size used for the update
    - ``n``: number of instances updated


-----



Copy to / from signals
------------------------

pre_copy_from_instances
~~~~~~~~~~~~~~~~~~~~~~~~~~

Fired just before ``copy_from_instances`` writes data to the database


Parameters:

    - ``instances``: a list of instances about to be updated


post_copy_from_instances
~~~~~~~~~~~~~~~~~~~~~~~~~~

Fired just after ``copy_from_instances`` writes data to the database

Parameters:

    - ``instances``: a list of instances that have been updated

