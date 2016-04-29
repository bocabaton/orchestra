import logging
from routes import Mapper
from pyengine.lib import config
from pyengine.lib.error import *

class Router:
    
    logger = logging.getLogger(__name__)

    ROUTER_CONF = config.getRouterConfig()
    INFO_META = ['module', 'sub_module', 'api_class', 'api_version']

    map = Mapper()

    def __init__(self):
        with self.map.submapper(path_prefix=self.ROUTER_CONF['URL_PREFIX'], module=self.ROUTER_CONF['MODULE']) as m:
            for u in self.ROUTER_CONF['URLS']:
                m.connect(None, u[1], sub_module=u[0], api_class=u[3], conditions=dict(method=[u[2]]))

    def match(self, request):
        api_request = {}
        api_request[u'meta'] = {}
        api_request[u'params'] = {}

        # RESTful URL Match
        result = self.map.match(request.path, {'REQUEST_METHOD': request.method})

        if result == None:
            # Error : Undefined URL
            raise ERROR_INVALID_REQUEST(url=request.path, method=request.method)

        for k in result.keys():
            if k in self.INFO_META:
                api_request['meta'][unicode(k)] = result[k]
            else:
                api_request['params'][unicode(k)] = result[k]

        return api_request
