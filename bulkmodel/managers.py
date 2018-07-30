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
        """
        Builds a queryset from a set of objects.
        For objects with a property called "id" or "pk" will be fetching from the database
        and populated with provided values.

        Objects missing these propertie will be created in bulk and re-fetched from the database

        :param collections.Iterable objects:
        :return:
        """
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
            new_records = self.model.objects.bulk_create(new_instances)
            _ids.extend([i.id for i in new_records])

        qs = self.model.objects.filter(id__in = _ids)

        if existing_instances:
            qs = qs.update_fields(existing_instances, return_queryset=True)

        return qs


    def populate_values(self, objects, *fieldnames):
        """
        Sets values on objects in the existing queryset from a given set of objects and optional set of fieldnames

        :param collections.Iterable objects: a list of objects with data to use as a source for updates to apply within the queryset
        :param List[str] fieldnames: a list of field names to apply updates to. If blank all fields will be updated
        :return:
        """
        return self.get_queryset().populate_values(objects, *fieldnames)



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

    def update_fields(self, *fieldnames, objects=None, batch_size=None, send_signal=True,
                      concurrent=False, max_concurrent_workers=None, return_queryset=False):
        """
        Performs a hetergeneous update

        :param fieldnames:
        :param objects:
        :param batch_size:
        :param send_signal:
        :param concurrent:
        :param max_concurrent_workers:
        :return:
        """
        return self.get_queryset().update_fields(
            *fieldnames, objects = objects, send_signal=send_signal,
            concurrent=concurrent, max_concurrent_workers=max_concurrent_workers,
            return_queryset = return_queryset
        )


    def bulk_create(self, objs, bm_create_uuid=None, batch_size=None, send_signal=True,
                    concurrent=False, max_concurrent_workers=None,
                    return_queryset=False):
        """
        A signal-enabled override of django's bulk_create

        :param objs:
        :param UUID bm_create_uuid: a uuid to use as the bm_create_uuid in the model
        :param batch_size:
        :param bool send_signal:
        :param bool concurrent:
        :param bool max_concurrent_workers:
        :param bool return_queryset: whether to return instances; if false, returns the default from django's method
        :return:
        """
        return self.get_queryset().bulk_create(
            objs, bm_create_uuid=bm_create_uuid, batch_size=batch_size, send_signal=send_signal,
            concurrent=concurrent, max_concurrent_workers=max_concurrent_workers,
            return_queryset=return_queryset
        )

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



    def copy_from_objects(self, objs, bm_create_uuid=None, exclude_id=True, signal=True,
                          concurrent=False, max_concurrent_workers=None,
                          fieldnames=None, batch_size=None,
                          return_queryset=False):
        """
        Updates data in the databse using the COPY FROM operaiton, if supported by the database being used

        :param objs:
        :param bm_create_uuid:
        :param exclude_id:
        :param signal:
        :param concurrent:
        :param max_concurrent_workers:
        :param fieldnames:
        :param batch_size:
        :param return_queryset:
        :return:
        """
        return self.get_queryset().copy_from_objects(
            objs, bm_create_uuid=bm_create_uuid, exclude_id=exclude_id, signal=signal,
            concurrent=concurrent, max_concurrent_workers=max_concurrent_workers,
            fieldnames=fieldnames, batch_size=batch_size,
            return_queryset=return_queryset
        )

