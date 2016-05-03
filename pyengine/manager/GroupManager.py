from pyengine.lib import utils
from pyengine.lib.error import *
from pyengine.manager import Manager 

class GroupManager(Manager):

    def createGroup(self, params):
        group_dao = self.locator.getDAO('group') 

        if group_dao.isExist(name=params['name']):
            raise ERROR_EXIST_RESOURCE(key='name', value=params['name'])

        dic = {}
        dic['name'] = params['name']

        if params.has_key('description'):
            dic['description'] = params['description']

        group = group_dao.insert(dic)

        return self.locator.getInfo('GroupInfo', group)

    def updateGroup(self, params):
        group_dao = self.locator.getDAO('group') 

        if not group_dao.isExist(uuid=params['id']):
            raise ERROR_INVALID_PARAMETER(key='id', value=params['id'])

        dic = {}

        if params.has_key('name'):
            dic['name'] = params['name']

        if params.has_key('description'):
            dic['description'] = params['description']

        group = group_dao.update(params['id'], dic)

        return self.locator.getInfo('GroupInfo', group)

    def deleteUser(self, params):
        group_dao = self.locator.getDAO('group') 

        groups = group_dao.getVOfromKey(uuid=params['id'])

        if groups.count() == 0:
            raise ERROR_NOT_FOUND(key='id', value=params['id'])

        groups.delete()

        return {}

    def getUser(self, params):
        group_dao = self.locator.getDAO('group')

        groups = group_dao.getVOfromKey(uuid=params['id'])

        if groups.count() == 0:
            raise ERROR_NOT_FOUND(key='id', value=params['id'])

        return self.locator.getInfo('GroupInfo', groups[0])

    def listGroups(self, search, search_or, sort, page, res_params):
        group_dao = self.locator.getDAO('group')

        if len(res_params) > 0:
            related_child = []

            for p in res_params:
                if p == 'user_count':
                    related_child.append('user')
        else:
            # DAO - Join Example
            # child_model = ['<model_name>']
            related_child = ['user']

        output = []
        (groups, total_count) = group_dao.select(search=search, search_or=search_or, sort=sort, page=page, related_child=related_child)

        for group in groups:
            group_info = self.locator.getInfo('GroupInfo', group, res_params=res_params)
            output.append(group_info)

        return (output, total_count)
