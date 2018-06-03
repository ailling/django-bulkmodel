Django Bulkmodel
=====================================

This projects adds a number of features missing from Django's ORM. It enables heterogeneous updates,
concurrent writes, retrieving records after bulk-creating them, and offline connection management to name a few
features it provides.


.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   pages/installation
   pages/overview-all-features


----


What BulkModel does, by example
---------------------------------

Suppose you have the following model::

    from bulkmodel.models import BulkModel

    class Foo(BulkModel):
        name = models.CharField(max_length=50, blank=False)
        value = models.IntegerField(null=False)


Some things you can do:

**Retrieve bulk-created model instances**

.. code-block:: python

    from random import randint, random, string

    ls = []
    for i in range(10):
        ls.append(Foo(
            # random string
            name = ''.join(random.choices(string.ascii_uppercase, 25)),

            # random value
            value = randint(0, 1000),
        ))

    # create instances and return a queryset of the created items
    foos = Foo.objects.bulk_create(ls, return_queryset=True)


**Heterogeneously update data**

The ``.update()`` method on a queryset performs a *homogeneous* update. That is, one or more columns for
all the records in the queryset are updated to the same value.

Django-bulkmodel lets you set different values for different primary keys, with a simple and intuitive API,
by introducing a method on a queryset called ``update_fields()``.

.. code-block:: python

    for foo in foos:
        foo.value += randint(100, 200)

    # update all fields that changed
    foos.update_fields()

    # or update just the value field
    foos.update_fields('value')


**Concurrent writes**

The ``batch_size`` flag that ships with django inserts data synchronously, blocking on each batch to be written into the database.

If your database hardware is sufficient and you're on Python 3.4+ you can decrease overall write time by batch
inserting concurrently. With django-bulkmodel you simply turn on the ``concurrency`` flag into any write operation.


.. code-block:: python

    foos = ...

    # concurrently write foos into the database
    Foo.objects.bulk_create(foos, concurrent=True, batch_size=1000, max_concurrent_workers=10)

    # a regular (homogeneous) update can be written concurrently
    foos.update(concurrent=True, batch_size=1000, max_concurrent_workers=10)

    # and so can a heterogeneous update
    foos.update_fields(concurrent=True, batch_size=1000, max_concurrent_workers=10)



-----


.. toctree::
   :maxdepth: 2
   :numbered:
   :caption: In-Depth Guides

   pages/bulk-create
   pages/bulk-update
   pages/concurrent-writes
   pages/connection-management
   pages/copy-to-from
   pages/signals


-----


.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/queryset
   reference/signals
   reference/helpers
   reference/concurrency-executor


-----



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
