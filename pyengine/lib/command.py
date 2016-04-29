import abc
import logging
import pytz
from datetime import datetime
from django.utils.dateparse import parse_datetime
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.lib.locator import Locator

class Command(object):

    __metaclass__ = abc.ABCMeta

    VAR_TYPE = {
        'bool' : type(bool()),
        'str' : type(str()),
        'int' : type(int()),
        'float' : type(float()),
        'dic' : type(dict()),
        'list' : type(list()),
        'tuple' : type(tuple()),
        'unicode' : type(unicode()),
        'any' : None,
    }

    # Every API specify valid parameters
    # Override in xxxCommand
    req_params = {}

    logger = logging.getLogger(__name__)
    locator = Locator()

    GLOBAL_CONF = config.getGlobalConfig()

    def __init__(self, api_request):
        self.user_meta = api_request['meta']['user']
        self.plugins = api_request['meta']['plugin']
        self.params = self._checkParam(api_request['params'])

    def _checkParam(self, api_params):
        """
        @param param : request parameters from Service API
        @return : update self.params
        """
        params = {}

        for key in self.req_params:
            # Key Exists
            if api_params.has_key(key):
                # Check Variable Type
                if self.VAR_TYPE[self.req_params[key][1]] == type(api_params[key]) or self.req_params[key][1] == 'any':
                    params[key] = api_params[key]

                else:
                    # Convert Unicode to String
                    if self.req_params[key][1] == 'str' and type(api_params[key]) == self.VAR_TYPE['unicode']:
                        params[key] = api_params[key].encode('utf-8')

                    else:
                        raise ERROR_INVALID_PARAM_TYPE(key=key, ptype=self.req_params[key][1])

                # Check Enum Value 
                if len(self.req_params[key]) >= 3:
                    if not api_params[key] in self.req_params[key][2]:
                        raise ERROR_INVALID_PARAMETER(key=key, value=str(self.req_params[key][2]))
                
            else:
                if self.req_params[key][0] == 'r':
                    raise ERROR_REQUIRED_PARAM(key=key)

        return params

    def makeSearch(self, *args):
        """
        Append search option with (k, params[k],"eq")
        """
        search = self.params.get('search', [])

        for k in args:
            if self.params.has_key(k) == True:
                additional = {'key':k, 'value':self.params[k], 'option':'eq'}
                search.append(additional)

        # Convert Timezone
        tz = pytz.timezone(self.user_meta['timezone'])

        for s in search:
            if s['key'] in self.GLOBAL_CONF['DATETIME_FIELDS']:
                try:
                    s['value'] = tz.localize(parse_datetime(s['value']), is_dst=None)
                except Exception as e:
                    self.logger.debug(e)
                    raise ERROR_INVALID_TIME_FORMAT() 

        return search

    def rollback(self):
        """
        Override in API rollback process
        """
        pass

    @abc.abstractmethod
    def execute(self):
        """
        Override in API implementation
        """
        pass
