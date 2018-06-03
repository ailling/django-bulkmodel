Overview of All Features
================================

The goal of django-bulkmodel is to expand on Django's ORM so that it's better suited for interacting with bulk data.


1. **Updating data heterogeneously**

    The ``update()`` method that ships with Django applies a **homogeneous update**. That is, all model instances
    in the queryset are updated to the be same value for the columns specified.

    A BulkModel includes a new method named ``update_fields()``, which allows you to update the database
    with different values for each model instance in the queryset through a single query execution.

    For more details see :doc:`bulk update user guide </pages/bulk-update>` and the
    :doc:`queryset API reference </reference/queryset>`.


2. **Getting querysets of bulk-created data**

    Sometimes you need to create some data and then do some further processing on the created records.
    However the ``bulk_create`` method returns what the database returns: the number of records returned.

    A BulkModel allows you to optionally return the queryset of objects created. So unless you can predict
    the primary key ahead of time, or can uniquely identify the data being inserted from some other combination
    you won't be able to get back the inserted data as it's represented in the database, with an assigned primary key.

    For more details see the :doc:`bulk create user guide </pages/bulk-create>` and the
    :doc:`queryset API reference </reference/queryset>`.


3. **Concurrent writes**

    In many cases and with a sufficiently capable database server you can accelerate bulk loading of data
    into the database by executing a concurrent write.

    BulkModels make this very easy-- exposing three parameters to give you full control over how your writes are constructed.

    In each queryset write method (which includes ``bulk_create``, ``copy_from_objects``, ``update`` and ``update_fields``)
    has the following parameters:

    - ``batch_size``: The size of each chunk to write into the database; this parameter can be used with or without concurrency
    - ``concurrent``: If true, a write will happen concurrently. The default is False
    - ``max_concurrent_workers``: The total number of concurrent workers involved in the event loop.

    For more details see the :doc:`concurrent writes user guide </pages/concurrent-writes>` and the
    :doc:`queryset API reference </reference/queryset>`.


4. **Offline connection management**

    Django manages the database connection inside a request / response cycle. A BulkModel is expecting data
    to be interacted with "offline" (meaning outside of the webserver) and checks or refreshes the connection if
    necessary when interacting with data in bulk.

    You can force a database connection check / refresh with the ``ensure_connected()`` queryset method.

    For more details see the :doc:`connection management user guide </pages/connection-management>` and the
    :doc:`queryset API reference </reference/queryset>`.


5. **Missing signals**

    Django ships with the following signals for interacting with data:

    - Saving a single instance: ``pre_save`` and ``post_save``
    - Deleting data: ``pre_delete`` and ``post_delete``
    - Changing a many to many relationship: ``m2m_changed``

    What's missing from this list are signals when data is created in bulk and updated in bulk.

    A BulkModel adds these signals and optionally lets you turn them off when calling any bulk write function.

    For more details see the :doc:`signals user guide </pages/signals>` and the
    :doc:`signals reference </reference/signals>`.


6. **Copying data to / from buffers**

    A BulkModel allows you write and read data by copying from and to a buffer, for databases that support it.

    For details on how to do this see the :doc:`copy to/from user guide </pages/signals>` and the
    :doc:`queryset API reference </reference/queryset>`.

