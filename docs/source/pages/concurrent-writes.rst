Concurrent writes
====================

Django comes with a ``batch_size`` parameter on the ``bulk_create`` queryset method.

Django-bulkmodel expands on the concept of batching in two ways:

- Batching is enabled on all write methods, including ``update()`` and ``update_fields()``
- You can optionally write data concurrently and specify a number of workers that makes sense for your database server and data size


Note that performance of concurrent writes won't increase linearly. In fact, if your database is constrained
with CPU resources, it's not likely to impact performance at all and could actually slow down your write.

This is an advanced feature that should be used with care. However you can improve write performance dramatically
when used correctly.

Parameters
------------

All database write methods have the following options to control concurrent writes:

- ``concurrent``: Set to true to enable concurrent writes. False by default
- ``batch_size``: Number of records to include in a single write (applies whether writing synchronous or asynchronous)
- ``max_concurrent_workers``: Maximum number of concurrent writers to use to apply the database operation



-----------



See :doc:`Queryset API Reference </reference/queryset>` for more details.
