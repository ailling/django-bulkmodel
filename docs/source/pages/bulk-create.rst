Bulk Create
=============

Django ships with a ``bulk_create`` method that supports a batch_size parameter for batch writing.

Django-bulkmodel expands on this queryset method with some new options.


Returning queryset
--------------------------------

Creating data in bulk returns what the database returns: the number of records created.

However there many cases where you want to obtain the created records for further manipulation, and
there's no way to do with this without have the primary keys associated with each record.

Django-bulkmodel exposes a parameter called ``return_queryset`` which returns created data as a queryset.


.. code-block:: python

    from random import randint, random, string
    from bulkmodel.models import BulkModel

    class Foo(BulkModel):
        name = models.CharField(max_length=50, blank=False)
        value = models.IntegerField(null=False)

    foo_objects = []
    for i in range(10):
        foo_objects.append(Foo(
            # random string
            name = ''.join(random.choices(string.ascii_uppercase, 25)),

            # random value
            value = randint(0, 1000),
        ))

    # create instances and return a queryset of the created items
    foos = Foo.objects.bulk_create(foo_objects, return_queryset=True)


Writing data by copying from a buffer
--------------------------------------

Bulk create will perform several inserts. Depending on your schema and database it may be faster to load
data from a path or buffer.

For supported databases, a BulkModel queryset exposes this functionality.


.. code-block:: python

    foos = []
    for i in range(10):
        foos.append(Foo(
            # random string
            name = ''.join(random.choices(string.ascii_uppercase, 25)),

            # random value
            value = randint(0, 1000),
        ))

    foos = Foo.objects.copy_from_objects(ls, return_queryset=True)

The ``return_queryset`` is available on all write methods. See the :doc:`Queryset Reference </reference/queryset>` for more details.



Missing signals
--------------------------------

A ``BulkModel`` adds several signals, including signals around creating data in bulk.

These signals are coupled to the two methods of creating data, as documented above:

- ``pre_bulk_create`` / ``post_bulk_create``: signals fired when data is created from ``bulk_create``
- ``pre_copy_from_instances`` / ``post_copy_from_instances``: signals fired when data is created using ``copy_from_objects``


You can optionally turn off emitting signals when creating data.

.. code-block:: python

    foo_objects = ...

    # do not send signals (the default is True)
    Foo.objects.bulk_create(foo_objects, send_signals=False)


For more information see the :doc:`signals user guide </pages/signals>` or the :doc:`signals API reference </reference/signals>`.


-----


Concurrent writes
--------------------------------

You can accelerate the loading of data by splitting work into batches and writing each batch concurrently.

A BulkModel queryset exposes three parameters to give you full control over this process:

- ``batch_size``: The size of each chunk to write into the database; this parameter can be used with or without concurrency
- ``concurrent``: If true, a write will happen concurrently. The default is False
- ``max_concurrent_workers``: The total number of concurrent workers involved in the event loop.


**Example**

.. code-block:: python

    foos = ...

    # concurrently write foos into the database
    Foo.objects.bulk_create(foos, concurrent=True, batch_size=1000, max_concurrent_workers=10)

    # a regular (homogeneous) update can be written concurrently
    foos.update(concurrent=True, batch_size=1000, max_concurrent_workers=10)

    # and so can a heterogeneous update
    foos.update_fields(concurrent=True, batch_size=1000, max_concurrent_workers=10)

For more information see the :doc:`concurrent writes user guide </pages/concurrent-writes>` or the :doc:`queryset API reference </reference/queryset>`.


