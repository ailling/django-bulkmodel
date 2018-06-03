Copy TO / FROM support
==================================================================

For database engines (i.e., Postgres) that support copying data into and out of a buffer
Django-bulkmodel exposes this functionality into the queryset.


There are now two methods you can call:

- ``copy_from_objects``: writes data from the provided list of objects to the database.
- ``copy_to_instances``: reads data out of a buffer and populates a list of objects

Examples
---------

Suppose you have the following model::

    from bulkmodel.models import BulkModel

    class Foo(BulkModel):
        name = models.CharField(max_length=50, blank=False)
        value = models.IntegerField(null=False)

Populate it with some data and use copy_from_objects to write the data into the database::

    ls = []
    for i in range(1000):
        ls.append(Foo(
            name = random_str(),
            value = randint(0, 1000),
        ))

    # returning the queryset is optional
    foos = Foo.objects.copy_from_objects(ls, return_queryset=True)


Likewise you can fetch data out the database by populating a list of objects from a buffer::

    objs = Foo.objects.copy_to_instances()
