import traceback, logging
from pyengine.lib import config
from pyengine.lib.error import *

class Plugin:

    logger = logging.getLogger(__name__)

    PLUGIN_CONF = config.getPluginConfig() 

    plugins = []

    def __init__(self):
        for p in self.PLUGIN_CONF['PLUGINS']: 
            p_module = __import__('pyengine.plugin.%s' %p, fromlist=[p])

            self.plugins.append(getattr(p_module, p)())

    def preload(self, api_request):
        api_request['meta']['plugin'] = {}

        for p in self.plugins:
            api_request = p.preload(api_request)

        return api_request

    def success(self, api_request, result):
        for p in self.plugins:
            result = p.success(api_request, result)

        return result

    def error(self, api_request, error):
        for p in self.plugins:
            p.error(api_request, error)
