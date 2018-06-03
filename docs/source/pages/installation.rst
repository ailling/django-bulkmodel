Installation and Getting Started
==========================================

Install the package from pypi::

    pip install django-bulkmodel

Add `bulkmodel` app to your `INSTALLED_APPS` list in settings.py::

    INSTALLED_APPS = [
        ...
        'bulkmodel',
    ]


Full Installation
-------------------------

Fully installing BulkModel requires inheriting your models from ``bulkmodel.models.BulkModel``::

    from django.db import models
    from bulkmodel.models import BulkModel

    class MyModel(BulkModel):
        ...


And migrate the database.


**Create migrations**

If you're creating a new app from scratch::

    ./manage.py makemigrations <name-of-your-app>

Do this for each new app you create that have BulkModels.


Otherwise, if this app already exists and has migrations::

    ./manage.py makemigrations


**Apply migrations**

And apply the migrations::

    ./manage.py migrate


Partial Installation
------------------------

If you don't want to migrate your database schema for whatever reason you can skip that step
and ``BulkModel`` will degrade gracefully. With this route you'll lose the ability
to retrieve a queryset after bulk creating data, and some signals will lose functionality.

With this route you'll need to point your ``objects`` reference on each ``BulkModel``.

.. code-block:: python

    from django.db import models
    from bulkmodel.models import BulkModel
    from bulkmodel.managers import BulkModelManager

    class MyModel(BulkModel):
        ...

        objects = BulkModelManager()


-------


Optional Settings
-------------------

Place the following in your ``settings.py`` to set global behavior of your bulkmodels:

- ``MAX_CONCURRENT_BATCH_WRITES``
When set, this is the maximum number of concurrent workers that will be available to any concurrent write across your entire project.
The default leaves this value unset.

- ``ALWAYS_USE_CONCURRENT_BATCH_WRITES``
If True, django-bulkmodel will always use concurrent writes. The default is False.

