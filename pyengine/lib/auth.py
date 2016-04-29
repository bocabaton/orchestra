import logging
from pyengine.lib import config
from pyengine.lib.system_client import SystemClient
from pyengine.lib.error import *

class Auth:
    
    logger = logging.getLogger(__name__)

    GLOBAL_CONF = config.getGlobalConfig()

    def verify(self, api_request):
        api_request['meta']['user'] = {}

        if api_request['meta']['sub_module'] in self.GLOBAL_CONF['NO_AUTH_MODULES']:
            return api_request

        elif api_request['meta']['sub_module'] in self.GLOBAL_CONF['SYSTEM_AUTH_MODULES']:
            return self._systemAuth(api_request)

        else:
            if self.GLOBAL_CONF['AUTH_TYPE'] == 'xauth':
                return self._xAuth(api_request)

            else:
                return self._noAuth(api_request)

    def _systemAuth(self, api_request):
        if not api_request['params'].has_key('system_key'):
            raise ERROR_AUTH_FAILED(reason = 'Required system key.')

        if api_request['params']['system_key'] != self.GLOBAL_CONF['SYSTEM_KEY']:
            raise ERROR_AUTH_FAILED(reason = 'System key is invalid.')

        api_request['meta']['user']['user_id'] = 'system'
        api_request['meta']['user']['permissions'] = '*'
        api_request['meta']['user']['timezone'] = self.GLOBAL_CONF['DEFAULT_TIMEZONE']

        return api_request

    def _xAuth(self, api_request):
        if not api_request['meta'].has_key('xtoken'):
            raise ERROR_AUTH_FAILED(reason = 'Required X-Auth-Token.')

        http_options = {}
        http_options['protocol'] = self.GLOBAL_CONF.get('AUTH_PROTOCOL', 'http')
        http_options['port'] = self.GLOBAL_CONF.get('AUTH_PORT', 80)

        sc = SystemClient(self.GLOBAL_CONF['AUTH_HOST'], **http_options)

        req_params = {}
        req_params['system_key'] = self.GLOBAL_CONF['SYSTEM_KEY']
        req_params['token'] = api_request['meta']['xtoken']
        response = sc.request('GET', self.GLOBAL_CONF['AUTH_URL'], params=req_params)

        if response['status'] == False:
            raise ERROR_AUTH_FAILED(reason = response['message'])

        api_request['meta']['user'] = response['response']

        return api_request

    def _noAuth(self, api_request):
        api_request['meta']['user']['user_id'] = 'anonymous'
        api_request['meta']['user']['permissions'] = 'all'
        api_request['meta']['user']['timezone'] = self.GLOBAL_CONF['DEFAULT_TIMEZONE']

        return api_request
