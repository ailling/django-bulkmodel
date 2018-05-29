from django.db import models
from django.db import InterfaceError
from django.db.utils import OperationalError
from django.db import connections
from io import StringIO
import collections


class BulkModelManager(models.Manager):

    def get_queryset(self):
        """
        Retrieves a queryset that refreshes the database connection when dropped
        The retry only happens once, and errors raised beyond this single retry attempt will be re-raised

        :return:
        """
        from .queryset import BulkModelQuerySet
        self.ensure_connected()
        return BulkModelQuerySet(self.model, using=self._db)


    def create_queryset(self, objects):
        if not isinstance(objects, collections.Iterable):
            return None

        if not objects:
            return self.get_queryset().none()

        _ids = []
        existing_instances = []
        new_instances = []

        for obj in objects:
            _id = getattr(obj, 'id') or getattr(obj, 'pk')
            if _id is not None:
                _ids.append(_id)
                existing_instances.append(obj)
            else:
                new_instances.append(obj)

        if new_instances:
            new_records = self.model.bulk_create(new_instances)
            _ids.extend([i.id for i in new_records])

        return self.model.objects.filter(id__in = _ids)


    def populate_values(self, objects):
        return self.get_queryset().populate_values(objects)



    def ensure_connected(self):
        """
        Makes sure the connection is established by running a select 1 against the cursor

        :return:
        """
        dbconn = connections[self.db]

        try:
            with dbconn.cursor() as c:
                c.execute('select 1;')

        except (OperationalError, InterfaceError):
            dbconn.close()



    def reset_connection(self):
        """
        Refreshes the connection by closing the existing one
        The next chained call in the queryset will open a new connection

        :return:
        """
        dbconn = connections[self.db]
        dbconn.close()

        return self


    # region wrappers so that it's easier for IDEs to pick up these queryset methods

    def update_fields(self, *fields, batch_size=None, send_signal=True,
                      concurrent=False, max_concurrent_workers=None):

        return self.get_queryset().update_fields(
            *fields, batch_size=batch_size, send_signal=send_signal,
            concurrent=concurrent, max_concurrent_workers=max_concurrent_workers
        )


    def bulk_create(self, *args, **kwargs):
        return self.get_queryset().bulk_create(*args, **kwargs)

    # endregion


    def copy_to_instances(self, columns=None):
        """
        Populates data in instances of the queryset using the COPY TO function, if supported by the
        database being used

        :param columns:
        :return:
        """
        dbconn = connections[self.db]
        tablename = self.model._meta.db_table
        ls = []

        buf = StringIO()

        with dbconn.cursor() as cursor:
            cursor.copy_to(buf, tablename, columns=columns)
            buf.seek(0,0)

        fields = self.model._meta.fields
        data = buf.read()
        buf.close()
        del buf

        rows = data.split('\n')
        for row in rows:
            if not row:
                continue

            cols = row.split('\t')
            objdata = {}
            for field, value in zip(fields, cols):
                objdata[field.name] = field.to_python(value)

            ls.append(self.model(**objdata))

        return ls



    def copy_from_objects(self, *args, **kwargs):
        return self.get_queryset().copy_from_objects(*args, **kwargs)

