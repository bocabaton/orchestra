from django.contrib.auth.hashers import make_password
from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 

class UserManager(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def createUser(self, params):
        user_dao = self.locator.getDAO('user') 

        if user_dao.isExist(user_id=params['user_id']):
            raise ERROR_EXIST_RESOURCE(key='user_id', value=params['user_id'])

        if not utils.checkIDFormat(params['user_id']):
            raise ERROR_INVALID_ID_FORMAT()

        if not utils.checkPasswordFormat(params['password']):
            raise ERROR_INVALID_PASSWORD_FORMAT()

        dic = {}
        dic['user_id'] = params['user_id']
        dic['password'] = make_password(params['password'])

        if params.has_key('name'):
            dic['name'] = params['name']

        if params.has_key('email'):
            dic['email'] = params['email']

        if params.has_key('language'):
            dic['language'] = params['language']
        else:
            dic['language'] = self.GLOBAL_CONF['DEFAULT_LANGUAGE']

        if params.has_key('timezone'):
            dic['timezone'] = params['timezone']
        else:
            dic['timezone'] = self.GLOBAL_CONF['DEFAULT_TIMEZONE']

        if params.has_key('group_id'):
            group_dao = self.locator.getDAO('group')

            groups = group_dao.getVOfromKey(uuid=params['group_id'])

            if groups.count() == 0:
                raise ERROR_INVALID_PARAMETER(key='group_id', value=params['group_id'])

            dic['group'] = groups[0]

        user = user_dao.insert(dic)

        return self.locator.getInfo('UserInfo', user)

    def updateUser(self, params):
        user_dao = self.locator.getDAO('user') 

        if not user_dao.isExist(user_id=params['user_id']):
            raise ERROR_INVALID_PARAMETER(key='user_id', value=params['user_id'])

        dic = {}

        if params.has_key('password'):
            if not utils.checkPasswordFormat(params['password']):
                raise ERROR_INVALID_PASSWORD_FORMAT()

            dic['password'] = make_password(params['password'])

        if params.has_key('name'):
            dic['name'] = params['name']

        if params.has_key('state'):
            dic['state'] = params['state']

        if params.has_key('email'):
            dic['email'] = params['email']

        if params.has_key('language'):
            dic['language'] = params['language']

        if params.has_key('timezone'):
            dic['timezone'] = params['timezone']

        if params.has_key('group_id'):
            group_dao = self.locator.getDAO('group')

            groups = group_dao.getVOfromKey(uuid=params['group_id'])

            if groups.count() == 0:
                raise ERROR_INVALID_PARAMETER(key='group_id', value=params['group_id'])

            dic['group'] = groups[0]

        user = user_dao.update(params['user_id'], dic, 'user_id')

        return self.locator.getInfo('UserInfo', user)

    def deleteUser(self, params):
        user_dao = self.locator.getDAO('user') 

        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])

        users.delete()

        return {}

    def enableUser(self, params):
        params['state'] = 'enable'

        return self.updateUser(params)

    def disableUser(self, params):
        params['state'] = 'disable'

        return self.updateUser(params)

    def getUser(self, params):
        user_dao = self.locator.getDAO('user')

        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])

        return self.locator.getInfo('UserInfo', users[0])

    def listUsers(self, search, search_or, sort, page, res_params):
        user_dao = self.locator.getDAO('user')

        if len(res_params) > 0:
            related_parent = []

            for p in res_params:
                if p == 'group_name':
                    related_parent.append('group')
        else:
            # DAO - Join Example
            # parent_model = ['<model_name>']
            # parent_parent_model = ['<model_name.model_name>']
            related_parent = ['group']

        output = []
        (users, total_count) = user_dao.select(search=search, search_or=search_or, sort=sort, page=page, related_parent=related_parent)

        for user in users:
            user_info = self.locator.getInfo('UserInfo', user, res_params=res_params)
            output.append(user_info)

        return (output, total_count)

    def addUserInfo(self, params):
        # TODO: encrypt password
        # TODO: Other user can not add user info
        user_dao = self.locator.getDAO('user')
        dao = self.locator.getDAO('user_detail')
        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])
        dic = {}
        dic['user'] = users[0]
        dic['platform'] = params['platform']
        items = params['add']
        for key in items.keys():
            dic['key'] = key
            dic['value'] = items[key]
            info = dao.insert(dic)
        return {}

    def getUserInfo(self, params):
        # TODO: decrypt password
        # TODO: Other user can not get user info
        dao = self.locator.getDAO('user_detail')

        user_dao = self.locator.getDAO('user')
        dao = self.locator.getDAO('user_detail')
        users = user_dao.getVOfromKey(user_id=params['get'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])

        search = [{'key':'user_id','value':params['get'],'option':'eq'},
                    {'key':'platform','value':params['platform'],'option':'eq'}]
        self.logger.debug("search:%s" % search)
        search_or = []
        sort = {}
        page = {}
        (items, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)
        output = {}
        for item in items:
            self.logger.debug(item)
            key = item.key
            value = item.value
            output[key] = value
        result = {}
        self.logger.debug("output:%s" % output)
        #TODO: for each platform, has specific format
        if params['platform'] == 'openstack':
            result['auth'] = {
                'tenantName':output['tenantName'],
                'passwordCredentials':{
                    'username':output['username'],
                    'password':output['password']
                }
            }
        elif params['platform'] == 'aws':
            result['auth'] = {
                'access_key_id':output['access_key_id'],
                'secret_access_key':output['secret_access_key']
                }

        elif params['platform'] == 'joyent':
            result['auth'] = {
                'key_id':output['key_id'],
                'secret':output['secret']
                }
 
        elif params['platform'] == 'bare-metal':
            # TODO: what should we do?
            pass

        return result

    ############################
    # Keypair
    ############################
    def addUserKeypair(self, params):
        # TODO: encrypt password
        # TODO: Other user can not add user info
        user_dao = self.locator.getDAO('user')
        dao = self.locator.getDAO('user_keypair')
        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])
        item = params['add']
        if item.has_key('name') == False:
            raise ERROR_REQUIRED_PARAM(key='add.name')
        if item.has_key('key_type') == False:
            raise ERROR_REQUIRED_PARAM(key='add.key_type')
        if item.has_key('value') == False:
            raise ERROR_REQUIRED_PARAM(key='add.value')

        dic = {}
        dic['user'] = users[0]
        dic['name'] = item['name']
        dic['key_type'] = item['key_type']
        dic['value'] = item['value']
        info = dao.insert(dic)
        return {}

    def getUserKeypair(self, params):
        dao = self.locator.getDAO('user_keypair')

        user_dao = self.locator.getDAO('user')
        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_NOT_FOUND(key='user_id', value=params['user_id'])

        search = [{'key':'name','value':params['get'],'option':'eq'}]
        self.logger.debug("search:%s" % search)
        search_or = []
        sort = {}
        page = {}
        (items, total_count) = dao.select(search=search, search_or=search_or, sort=sort, page=page)
        if total_count == 0:
            raise ERROR_NOT_FOUND(key='name', value=params['get'])
        item = items[0]
        output = {}
        output['name'] = item.name
        output['key_type'] = item.key_type
        output['value'] = item.value
        return output
