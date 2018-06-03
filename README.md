# Django BulkModel

BulkModel adds additional features that makes it easier to interact with data in bulk.

Below is a brief summary of the project. Read the [full documentation](https://django-bulkmodel.readthedocs.io/)

---


## BulkModels and features

Create a bulkmodel by inheriting from `BulkModel`:

    from bulkmodel.models import BulkModel

    class Foo(BulkModel):
        name = models.CharField(max_length=50, blank=False)
        value = models.IntegerField(null=False)


Here's some new functionality that's available to you now:

### 1) Get a queryset after a bulk create

Sometimes you need created data to be returned from the database
with a primary key assigned to each model instance for full processing.

This is typically the case when you bulk create some data and then
want to assign foreign keys to other models, thereby requiring the primary keys
on the new data.


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


### 2) Heterogeneous updates

Django's `update()` queryset method allows you to update **homogeneous data**.

That is, all the model instances in the queryset are updated to the same value (or applied
the same change when using F expressions) for the specified columns.

BulkModels allow you to update data **heterogeneously**. That is,
each model instance in a queryset can take on a different value in a single query execution.

To do this, use the `update_fields()` queryset method, like so:

    for foo in foos:
        foo.value += randint(100, 200)

    # update all fields that changed
    foos.update_fields()

    # or update just the value field
    foos.update_fields('value')

This will only execute one query, regardless of how many fields are in the model are updated.


### 3) Concurrent writes

BulkModels support concurrent writes out of the box, which can significantly
speed up write time given a large enough database server.

Concurrent writes are available on all the write queryset methods
(`bulk_create`, `update`, `update_fields`, `copy_from_objects`).

    foos = ...

    # concurrently write foos into the database
    Foo.objects.bulk_create(foos, concurrent=True, batch_size=1000, max_concurrent_workers=10)

    # a regular (homogeneous) update can be written concurrently
    foos.update(concurrent=True, batch_size=1000, max_concurrent_workers=10)

    # and so can a heterogeneous update
    foos.update_fields(concurrent=True, batch_size=1000, max_concurrent_workers=10)


### 4) Additional signals

Django ships with the following signals for interacting with data:

- Saving a single instance: `pre_save` and `post_save`
- Deleting data: `pre_delete` and `post_delete`
- Changing a many to many relationship: `m2m_changed`

What's missing from this list are signals when data is created in bulk and updated in bulk.

BulkModels ship with additional signals when data is created:


- `pre_bulk_create` / `post_bulk_create` are fired when data is being written from `bulk_create`
- `pre_copy_from_instances` / `post_copy_from_instances` are fired when data is being written from a data buffer (via the `copy_from_objects` queryset method)


And these signals when data is updated:

- `pre_update` / `post_update` are fired when a homogeneous update is applied
- `pre_update_fields` / `post_update_fields` are fired when a heterogeneous update is applied


You can optionally turn off signal emission in any write function by setting `send_signals=False`
(signals are emitted by default).

### 5) More

A few more features come with BulkModels, like offline connection management,
copying data to and from the database via in-memory buffers, and queryset chunking.

[See the full list of features](https://django-bulkmodel.readthedocs.io/en/latest/pages/overview-all-features.html)

---

## Installation

First make sure you have django >= 1.9 installed. It's always
recommended to update to the latest version of Django.

For concurrency features to work you'll need Python 3.4+ and access to asyncio

Then install the package from pypi:

    pip install django-bulkmodel

Add `bulkmodel` to your `INSTALLED_APPS`:

    INSTALLED_APPS = [
        ...
        'bulkmodel',
    ]


Inherit your existing models from `BulkModel`, or create new models to inherit
from this class:

    from django.db import models
    from bulkmodel.models import BulkModel

    class MyModel(BulkModel):
        ...


Make migrations:

    ./manage.py makemigrations <name-of-your-app> # for new apps
    ./manage.py makemigrations # for existing apps with migrations

And apply them:

    ./manage.py migrate


You can also do a partial installation if you don't want to migrate all your models.

For more instructions [read the full installation instructions documentation](https://django-bulkmodel.readthedocs.io/en/latest/pages/installation.html)



---

## Full documentation

[Read the full documentation](https://django-bulkmodel.readthedocs.io/)

## License

This software is made available under the Apache v2 License; see the LICENSE file for details.

