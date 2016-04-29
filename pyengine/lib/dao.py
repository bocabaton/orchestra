import uuid
import logging
from datetime import datetime
from django.db.models import Q
from pyengine.lib.error import *

class DAO:

    logger = logging.getLogger(__name__)

    def __init__(self, model):
        self.model = model

    def insert(self, dic): 
        for field in self.model._meta.fields:
            if dic.has_key(field.name):
                if field.unique == True:
                    filter = {field.name: dic[field.name]}
                    vos = self.model.objects.filter(**filter)

                    if vos.count() > 0:
                        raise ERROR_NOT_UNIQUE(value=dic[field.name] ,field=field.name)
            else:
                if field.name not in ['id','created','last_update'] and str(field.default) == 'django.db.models.fields.NOT_PROVIDED':
                    raise ERROR_REQUIRED_FIELD(field=field.name)

                if str(field.default) == 'custom_id':
                    dic[field.name] = self._createCustomID(field.name, field.help_text)

        insert_model = self.model(**dic)
        insert_model.save()

        return insert_model

    def _createCustomID(self, field_name, id_prefix):
        i = 0

        while True:
            custom_id = '%s-%s' %(id_prefix, str(uuid.uuid4())[:8])

            if i == 10:
                raise ERROR_ID_GENERATION_FAILED()

            filter = {field_name: custom_id}
            vos = self.model.objects.filter(**filter)
            if vos.count() == 0:
                break

            i += 1

        return custom_id

    def update(self, value, dic, update_key='uuid'):
        update_key_filter = {update_key: value}

        for d in dic:
            try:
                field = self.model._meta.get_field(d)
            except Exception as e:
                raise ERROR_UNKNOWN_FIELD(field=d)

            if field:
                if field.unique == True:
                    filter = {field.name: dic[field.name]}

                    vos = self.model.objects.filter(**filter).exclude(**update_key_filter)
                    if vos.count() > 0:
                        raise ERROR_NOT_UNIQUE(value=dic[field.name] ,field=field.name)

        for f in self.model._meta.fields:
            if f.name in ['last_update']:
                dic[f.name] = datetime.now() 

        self.model.objects.filter(**update_key_filter).update(**dic)

        return self.getVOfromKey(**update_key_filter)[0]

    def delete(self, value, delete_key='uuid'):
        delete_key_filter = {delete_key: value}

        self.model.objects.filter(**delete_key_filter).delete()

    def getValuefromKey(self, field, **filter):
        value_list = []

        vos = self.model.objects.filter(**filter)
        for vo in vos:
            value_list.append(vo.__dict__[field])

        return value_list

    def getVOfromKey(self, **filter):
        vos = self.model.objects.filter(**filter)

        return vos

    def getVOAll(self):
        vos = self.model.objects.all()

        return vos

    def isExist(self, **filter):
        vos = self.getVOfromKey(**filter)
        if vos.count() == 0:
            return False
        else:
            return True

    def select(self, **kwargs):
        filter = {}
        not_filter = {}
        filter_or = []
        or_query = None
        order_by = None
        distinct = None
        related_parent = []
        related_child = []

        if kwargs.has_key('search'):
            for s in kwargs['search']:
                if s.has_key('key') and s.has_key('value') and s.has_key('option'):
                    if s['option'] == 'contain':
                        filter['%s__icontains' %str(s['key'])] = s['value']
                    elif s['option'] == 'lt':
                        filter['%s__lt' %str(s['key'])] = s['value']
                    elif s['option'] == 'lte':
                        filter['%s__lte' %str(s['key'])] = s['value']
                    elif s['option'] == 'gt':
                        filter['%s__gt' %str(s['key'])] = s['value']
                    elif s['option'] == 'gte':
                        filter['%s__gte' %str(s['key'])] = s['value']
                    elif s['option'] == 'eq':
                        filter[str(s['key'])] = s['value']
                    elif s['option'] == 'in':
                        if type(s['value']) == type(list()):
                            filter['%s__in' %str(s['key'])] = s['value']
                    elif s['option'] == 'not':
                        not_filter[str(s['key'])] = s['value']
                    elif s['option'] == 'ncontain':
                        not_filter['%s__icontains' %str(s['key'])] = s['value']
                    elif s['option'] == 'notin':
                        if type(s['value']) == type(list()):
                            not_filter['%s__in' %str(s['key'])] = s['value']

        if kwargs.has_key('search_or'):
            for s in kwargs['search_or']:
                if s.has_key('key') and s.has_key('value') and s.has_key('option'):
                    if s['option'] == 'contain':
                        filter_or.append(Q(**{'%s__icontains' %str(s['key']): s['value']}))
                    elif s['option'] == 'lt':
                        filter_or.append(Q(**{'%s__lt' %str(s['key']): s['value']}))
                    elif s['option'] == 'lte':
                        filter_or.append(Q(**{'%s__lte' %str(s['key']): s['value']}))
                    elif s['option'] == 'gt':
                        filter_or.append(Q(**{'%s__gt' %str(s['key']): s['value']}))
                    elif s['option'] == 'gte':
                        filter_or.append(Q(**{'%s__gte' %str(s['key']): s['value']}))
                    elif s['option'] == 'eq':
                        filter_or.append(Q(**{str(s['key']): s['value']}))
                    elif s['option'] == 'in':
                        if type(s['value']) == type(list()):
                            filter_or.append(Q(**{'%s__in' %str(s['key']): s['value']}))
                    elif s['option'] == 'not':
                        filter_or.append(~Q(**{str(s['key']): s['value']}))
                    elif s['option'] == 'ncontain':
                        filter_or.append(~Q(**{'%s__icontains' %str(s['key']): s['value']}))
                    elif s['option'] == 'notin':
                        if type(s['value']) == type(list()):
                            filter_or.append(~Q(**{'%s__in' %str(s['key']): s['value']}))

        if kwargs.has_key('sort'):
            sort = kwargs['sort']
            if sort.has_key('key'):
                if sort.has_key('desc') and sort['desc'] == True:
                    order_by = '-%s' %str(sort['key'])
                else:
                    order_by = '%s' %str(sort['key'])

        if kwargs.has_key('related_parent'):
            related_parent = [key.replace('.', '__') for key in kwargs['related_parent']]

        if kwargs.has_key('related_child'):
            related_child = ['%s_set'%(key) for key in kwargs['related_child']]

        if kwargs.has_key('distinct'):
            distinct = kwargs['distinct']

        try:
            vos = self.model.objects.filter(**filter)

            if len(filter_or) > 0:
                for or_condition in filter_or:
                    if or_query == None: 
                        or_query = or_condition
                    else:
                        or_query = or_query | or_condition

                vos = vos.filter(or_query)

            if not_filter != {}:
                vos = vos.exclude(**not_filter)

            if len(related_parent) > 0:
                vos = vos.select_related(*related_parent)

            if len(related_child) > 0:
                vos = vos.prefetch_related(*related_child)

            if order_by:
                vos = vos.order_by(order_by)

            if distinct:
                vos = vos.values(distinct).distinct()

            total_count = vos.count()

            if kwargs.has_key('page'):
                page = kwargs['page']
                if page.has_key('limit'):
                    if page.has_key('start'):
                        vos = vos[(page['start'] - 1):(page['start'] + page['limit'] - 1)]
                    else:
                        vos = vos[0:page['limit']]

            return (vos, total_count)

        except Exception as e:
            raise ERROR_QUERY_FAILED(reason=e)
