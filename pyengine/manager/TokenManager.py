import time
import uuid
from datetime import datetime
from django.contrib.auth.hashers import check_password
from pyengine.lib import config
from pyengine.manager import Manager 
from pyengine.lib.error import *

class TokenManager(Manager):

    GLOBAL_CONF = config.getGlobalConfig()

    def getToken(self, params):
        user_dao = self.locator.getDAO('user') 
        token_dao = self.locator.getDAO('token')

        users = user_dao.getVOfromKey(user_id=params['user_id'])

        if users.count() == 0:
            raise ERROR_INVALID_PASSWORD()

        user = users[0]
        
        if not check_password(params['password'], user.password):
            raise ERROR_INVALID_PASSWORD()

        if user.state == 'disable':
            raise ERROR_NO_PERMISSIONS()

        dic = {}
        dic['user'] = user

        token = token_dao.insert(dic)

        return {'token': str(token.token)}

    def expireToken(self, params):
        token_dao = self.locator.getDAO('token')

        timeout_ts = int(time.time()) - int(self.GLOBAL_CONF['TOKEN_EXPIRE_TIME'])

        search = [{'key':'created', 'value':datetime.fromtimestamp(timeout_ts), 'option':'lt'}]

        (tokens, total_count) = token_dao.select(search=search)

        tokens.delete()

        return {}

    def authToken(self, params):
        token_dao = self.locator.getDAO('token')
        timeout_ts = int(time.time()) - int(self.GLOBAL_CONF['TOKEN_EXPIRE_TIME'])

        try:
            token_uuid = uuid.UUID(params['token'])
        except:
            raise ERROR_INVALID_TOKEN()
        
        search = []
        search.append({'key':'created', 'value':datetime.fromtimestamp(timeout_ts), 'option':'gte'})
        search.append({'key':'token', 'value':token_uuid, 'option':'eq'})

        (tokens, total_count) = token_dao.select(search=search)

        if tokens.count() == 0:
            raise ERROR_INVALID_TOKEN()

        token = tokens[0]

        if token.user.state == 'disable':
            raise ERROR_NO_PERMISSIONS()

        dic = {}
        dic['user_id'] = token.user.user_id
        dic['permissions'] = '*'
        dic['timezone'] = token.user.timezone

        return dic
