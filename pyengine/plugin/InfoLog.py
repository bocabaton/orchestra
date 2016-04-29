from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.plugin import Plugin

class InfoLog(Plugin):

    INFOLOG_CONF = config.getPluginConfig()['InfoLog']

    def preload(self, api_request):
        if not api_request['meta']['api_class'] in self.INFOLOG_CONF['NO_PRINT_API']:
            self.logger.info("%s (Request)==> %s" %(api_request['meta']['api_class'], str(api_request['params'])))

        return api_request

    def success(self, api_request, result):
        if not api_request['meta']['api_class'] in self.INFOLOG_CONF['NO_PRINT_API']:
            self.logger.info("%s (Response)==> %s" %(api_request['meta']['api_class'], str(result)))

        return result
