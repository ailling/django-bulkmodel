Bulk Updates
=============

Django ships with an ``update()`` method to update data to the database.

This method is limited to updating data **homogeneously**-- that is, all the values
for the column(s) being updated is set to the *same value* throughout the queryset.

Django-bulkmodel adds to the functionality by providing a ``update_fields()`` method,
which updates data **heterogeneously**-- that is, the values for the column(s) being
updated can have different values for each model instance in the queryset.


Suppose you have the following model::

    from bulkmodel.models import BulkModel

    class Foo(BulkModel):
        name = models.CharField(max_length=50, blank=False)
        value = models.IntegerField(null=False)


Using ``update`` you can change the value to be the same

.. code-block:: python

    foos = ... # a queryset

    foos.update(value = 5)


Using ``update_fields`` you can update records to have different
values for each item.

.. code-block:: python

    for foo in foos:
        # different value for each model instance in the queryset
        foo.value += randint(100, 200)

    # update all fields that changed
    foos.update_fields()

    # or update just the value field
    foos.update_fields('value')


Importantly, this will issue a **single query** against the database.

-------

See :doc:`Queryset Reference </reference/queryset>` for more details.
