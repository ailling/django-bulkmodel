Frequency Asked Questions
==============================

Here are some frequently asked questions. If you have additional ones please send an email
to Alan at ``alanilling@protonmail.com``


How does django-bulkmodel change my models?
------------------------------------------------

It adds a field called ``bm_create_uuid`` an indexed UUID field, which is populated whenever data is created.

This way, it knows how to group created sets of data and return a queryset after bulk creating data.


What database engines are supported?
------------------------------------------------

Everything Django supports!

Django-bulkmodel doesn't write any custom SQL to do what it needs to do. It only engages with Django's
high-level ORM, which already abstracts out the differences between database engines.

The exception of course is anything that's only supported in one particular database. For example if you're
using a database that doesn't support copying data to and from buffers you won't be able to use the ``copy_from_objects``
or ``copy_to_instances`` methods.

