from django.db import models
from django.db.models import Case, Value, When
from .signals import (
    pre_update_fields,
    post_update_fields,
    pre_update,
    post_update,
    pre_bulk_create,
    post_bulk_create,
    pre_copy_from_instances,
    post_copy_from_instances,
)
from .ce import ConcurrentExecutor
import uuid
from django.conf import settings
from functools import partial
from django.db import connections
from io import StringIO
import collections


class BulkModelQuerySet(models.QuerySet):

    def _get_n_concurrent_workers(self, n, default=30):
        _max = getattr(settings, 'MAX_CONCURRENT_BATCH_WRITES', default)

        if _max:
            return max(n, _max)

        return n


    def _get_concurrent(self, flag, default=False):
        return flag or getattr(settings, 'ALWAYS_USE_CONCURRENT_BATCH_WRITES', default)


    def _update_chunk(self, chunk, **kwargs):
        pks = [i.pk for i in chunk]
        return self.filter(id__in = pks).update(_use_super=True, **kwargs)


    def populate_values(self, objects, *fieldnames):
        """
        Sets values on objects in the existing queryset from a given set of objects and optional set of fieldnames

        :param collections.Iterable objects: a list of objects with data to use as a source for updates to apply within the queryset
        :param List[str] fieldnames: a list of field names to apply updates to. If blank all fields will be updated
        :return:
        """
        if not isinstance(objects, collections.Iterable):
            raise TypeError('Must provide an iterable collection of objects')

        if not fieldnames:
            fieldnames = [i.name for i in self.model._meta.get_fields()]

        object_by_id = {
            getattr(obj, 'id') or getattr(obj, 'pk'): obj for obj in objects if getattr(obj, 'id') or getattr(obj, 'pk')
        }

        for instance in self:
            obj = object_by_id.get(instance.pk)
            if not obj:
                # no object found; cannot populate values for this instance
                continue

            for fieldname in fieldnames:
                if not hasattr(obj, fieldname):
                    raise AttributeError(f'Attribute {fieldname} does not exist on provided object: {obj}')

                setattr(instance, fieldname, getattr(obj, fieldname, None))

        return self



    def update(self, batch_size=None, concurrent=False, max_concurrent_workers=None,
               send_signals=True, _use_super=False, return_queryset=False, **kwargs):
        """
        Performs a homogeneous update of data.

        :param batch_size:
        :param concurrent:
        :param max_concurrent_workers:
        :param send_signals:
        :param _use_super:
        :param return_queryset:
        :return:
        """
        if _use_super:
            return super().update(**kwargs)

        if send_signals:
            pre_update.send(sender=self.model, instances = self)

        n_concurrent_writers = self._get_n_concurrent_workers(max_concurrent_workers)
        concurrent = self._get_concurrent(concurrent)

        chunks = self.get_chunks(batch_size, n_concurrent_writers)

        n = 0

        if concurrent:
            # question: how do you pass arguments in this function?
            jobs = [partial(BulkModelQuerySet._update_chunk, self, chunk, **kwargs) for chunk in chunks if chunk]
            executor = ConcurrentExecutor(jobs)
            results = executor.run_async()
            n = sum(results)

        else:
            for chunk in chunks:
                if not chunk:
                    # skip empty chunks (only happens in the case of an empty queryset)
                    continue

                n += self._update_chunk(chunk, **kwargs)

        if send_signals:
            post_update.send(sender = self.model, instances = self)

        if return_queryset:
            _ids = []
            for obj in self:
                _id = getattr(obj, 'id') or getattr(obj, 'pk')
                if _id:
                    _ids.append(_id)

            return self.filter(id__in = _ids)

        return n


    def _cased_update_chunk(self, chunk, fields):
        pks = [i.pk for i in chunk]
        cases = self._get_case_conditions(pks, fields)
        return self.filter(id__in = pks).update(**cases)



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
        :param return_queryset:
        :return:
        """
        if not fieldnames:
            fieldnames = [
                i.name for i in self.model._meta.fields
            ]

        if objects is not None:
            if not isinstance(objects, collections.Iterable):
                raise TypeError('objects must be iterable')

            self.populate_values(objects, *fieldnames)

        concurrent_write = self._get_concurrent(concurrent)

        if send_signal:
            pre_update_fields.send(
                self.model,
                instances = self,
                field_names = fieldnames,
                batch_size = batch_size
            )

        # TODO: ensure connected each time an update happens within the loop
        self.model.objects.ensure_connected()

        n = 0

        if concurrent_write:
            n_concurrent_writers = self._get_n_concurrent_workers(max_concurrent_workers)
            chunks = self.get_chunks(batch_size, n_concurrent_writers)

            jobs = [(BulkModelQuerySet._cased_update_chunk, self, chunk, fieldnames,) for chunk in chunks if chunk]
            executor = ConcurrentExecutor(jobs)
            results = executor.run_async()
            n = sum(results)

        else:
            chunks = self.get_chunks(batch_size)

            for chunk in chunks:
                if not chunk:
                    # skip empty chunks (only happens in the case of an empty queryset)
                    continue

                result = self._cased_update_chunk(chunk, fieldnames)
                n += result


        if return_queryset:
            _ids = []
            for obj in self:
                _id = getattr(obj, 'id') or getattr(obj, 'pk')
                if _id is not None:
                    _ids.append(_id)

            qs = self.filter(id__in = _ids)
        else:
            qs = self.none()


        if send_signal:
            post_update_fields.send(
                self.model,
                instances = self,
                queryset = qs,
                field_names = fieldnames,
                batch_size = batch_size,
                n = n
            )

        if return_queryset:
            return qs

        return n



    def get_chunks(self, chunk_size, max_chunks=None):
        """
        Splits the queryset results into chunks

        WARNING this method is destructive: it returns a list of lists,
        not a queryset. The queryset object will be lost

        :param chunk_size:
        :param max_chunks:
        :return:
        """
        from .helpers import get_chunks as chunker
        return chunker(self, chunk_size, max_chunks=max_chunks)



    def _get_field_when_conditions(self, fieldname, id_list):
        conditions = []

        for record in self:
            if record.pk is None:
                raise RuntimeError('Attempting to update an unsaved db record')

            if record.pk not in id_list:
                continue

            val = getattr(record, fieldname)
            if val is None:
                continue

            conditions.append(When(
                id = record.pk,
                then = Value(val)
            ))

        return conditions



    def _get_case_conditions(self, id_list, fieldnames):
        cases = {}

        for fieldname in fieldnames:
            field = self.model._meta.get_field(fieldname)
            defaultvalue = field.get_default()

            # get the when conditions for this field
            when_conditions = self._get_field_when_conditions(fieldname, id_list)

            cases[fieldname] = Case(*when_conditions, default = Value(defaultvalue))

        return cases



    def _degraded_bulk_create(self, objs, batch_size=None, send_signal=True):
        """
        A bulk-create that degrades to django's implementation but still sends additional signals

        :param objs:
        :param batch_size:
        :param send_signal:
        :return:
        """
        if send_signal:
            pre_bulk_create.send(self.model, instances=objs)

        result = super().bulk_create(objs, batch_size=batch_size)

        if send_signal:
            post_bulk_create.send(self.model, instances=objs)

        return result


    def _attach_bm_create_uuids(self, objs, bm_create_uuid):
        if bm_create_uuid is None:
            bm_create_uuid = uuid.uuid4()
        elif isinstance(bm_create_uuid, str):
            bm_create_uuid = uuid.UUID(bm_create_uuid)

        attached = set()
        for obj in objs:
            if not getattr(obj, 'bm_create_uuid'):
                setattr(obj, 'bm_create_uuid', bm_create_uuid)
            attached.add(getattr(obj, 'bm_create_uuid'))

        return attached



    def bulk_create(self, objs, bm_create_uuid=None, batch_size=None, send_signal=True,
                    concurrent=False, max_concurrent_workers=None,
                    return_queryset=False, **kwargs):
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
        is_bulkmodel = hasattr(self.model, 'bm_create_uuid')
        if is_bulkmodel:
            uuids = self._attach_bm_create_uuids(objs, bm_create_uuid)
        else:
            uuids = set()

        if send_signal:
            pre_bulk_create.send(sender=self.model, instances=objs)

        n_concurrent_writers = self._get_n_concurrent_workers(max_concurrent_workers)
        concurrent = self._get_concurrent(concurrent)

        if concurrent:
            chunks = self.get_chunks(batch_size, n_concurrent_writers)
            f = super().bulk_create

            jobs = [(f, chunk,) for chunk in chunks if chunk]
            executor = ConcurrentExecutor(jobs)
            result = executor.run_async()

        else:
            result = super().bulk_create(objs, batch_size=batch_size)

        if is_bulkmodel and return_queryset:
            qs = self.filter(bm_create_uuid__in = uuids)
        else:
            qs = self.none()

        if send_signal:
            post_bulk_create.send(sender=self.model, instances=objs, queryset=qs)

        if return_queryset:
            return qs

        return result



    def _copy_from_chunk(self, tablename, fieldnames, chunk):
        dbconn = connections[self.db]

        buf = StringIO()
        n_objects = len(chunk)
        n_fieldnames = len(fieldnames)

        for i, obj in enumerate(chunk):
            for j, fieldname in enumerate(fieldnames):
                val = getattr(obj, fieldname)
                if val is None:
                    vstr = '\\N'
                else:
                    vstr = str(val)

                buf.write(vstr)

                if j < n_fieldnames - 1:
                    buf.write('\t')

            if i < n_objects - 1:
                buf.write('\n')

        # rewind
        buf.seek(0,0)

        # iterate through the cursor and set \N for null
        with dbconn.cursor() as cursor:
            # run a copy from a cursor; note there's no need to commit here because there's no transaction
            cursor.copy_from(buf, tablename, columns=tuple(fieldnames), sep='\t', null='\\N')

        buf.close()
        del buf



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
        from .helpers import get_chunks

        is_bulkmodel = hasattr(self.model, 'bm_create_uuid')
        if is_bulkmodel:
            uuids = self._attach_bm_create_uuids(objs, bm_create_uuid)
        else:
            uuids = set()

        # get the field names
        if not fieldnames:
            fieldnames = [i.name for i in self.model._meta.get_fields()]

        tablename = self.model._meta.db_table

        if exclude_id:
            fieldnames = [i for i in fieldnames if i != 'id']

        if signal:
            pre_copy_from_instances.send(sender = self.model, instances=objs)

        n_concurrent_writers = self._get_n_concurrent_workers(max_concurrent_workers)
        concurrent = self._get_concurrent(concurrent)

        chunks = get_chunks(objs, batch_size, n_concurrent_writers)

        if concurrent:
            jobs = [(BulkModelQuerySet._copy_from_chunk, self, tablename, fieldnames, chunk) for chunk in chunks if chunk]
            executor = ConcurrentExecutor(jobs)
            executor.run_async()

        else:
            for chunk in chunks:
                if not chunk:
                    continue

                self._copy_from_chunk(tablename, fieldnames, chunk)


        if is_bulkmodel and return_queryset:
            qs = self.filter(bm_create_uuid__in = uuids)
        else:
            qs = self.none()

        if signal:
            post_copy_from_instances.send(sender = self.model, instances=objs)

        if return_queryset:
            return qs

        return None
