Signals
===============

Django `ships with <https://docs.djangoproject.com/en/2.0/topics/signals/>`_ the following signals for database operations:

- Saving a single instance: ``pre_save`` and ``post_save``
- Deleting data: ``pre_delete`` and ``post_delete``
- Changing a many to many relationship: ``m2m_changed``


Missing from this list is the ability to attach signals before and after updating data and bulk-creating data.

Bulk-create signals
--------------------

The following signals are fired when data is created in bulk:

- ``pre_bulk_create`` is fired just before data is created
- ``post_bulk_create`` is fired just after data is created


For copying data into the database from a buffer (i.e., using ``copy_from_instances``):

- ``pre_copy_from_instances`` is fired just before data is copied
- ``post_copy_from_instances`` is fired just after data is copied


Update signals
---------------

There are three sets of signals attached to the three ways you can update data.

For homogeneous updates (i.e., use the classic ``update()``):

- ``pre_update`` is fired just before data is updated
- ``post_update`` is fired just after data is updated


For heterogeneous updates (i.e., using ``update_fields()``):

- ``pre_update_fields`` is fired just before data is updated
- ``post_update_fields`` is fired just after data is updated


----------


See :doc:`Siganls Reference </reference/signals>` for more details.
