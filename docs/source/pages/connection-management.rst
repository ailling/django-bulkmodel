Connection Management
=========================

By default Django manages the connection within a request / response cycle.

Django-bulkmodel enables offline connection management, so that you won't lose your connection outside of this cycle.

To check or refresh your connection (if necessary), call ``ensure_connected()`` on your queryset.

Django-bulkmodel internally calls this method as appropriate.

Example
---------

.. code-block:: python

    foos = ... # some queryset
    foos.ensure_connected().filter(name = 'alice')


-----------


See :doc:`Queryset API Reference </reference/queryset>` for more details.

