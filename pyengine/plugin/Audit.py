import logging
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.lib.system_client import SystemClient
from pyengine.plugin import Plugin

class Audit(Plugin):

    AUDIT_CONF = config.getPluginConfig()['Audit']

    def preload(self, api_request):
        api_class = api_request['meta']['api_class']
        if self.AUDIT_CONF['AUDIT_API'].has_key(api_class):
            audit = BaseAudit(self.AUDIT_CONF['AUDIT_HOST'])

            audit.start(api_request, self.AUDIT_CONF['AUDIT_API'][api_class])

            api_request['meta']['plugin']['audit'] = audit

        return api_request

    def success(self, api_request, result):
        if api_request['meta']['plugin'].has_key('audit'):
            api_request['meta']['plugin']['audit'].success()

        return result

    def error(self, api_request, error):
        if api_request['meta']['plugin'].has_key('audit'):
            api_request['meta']['plugin']['audit'].error(error)


class BaseAudit:
    
    logger = logging.getLogger(__name__)

    def __init__(self, audit_host):
        self.sc = SystemClient(audit_host)

    def start(self, api_request, audit_info):
        if api_request['params'].has_key(audit_info[1]):
            self.logger.debug(audit_info[0] %(api_request['params'][audit_info[1]]))

    def update(self):
        self.logger.debug('Update Event')
        pass

    def success(self):
        self.logger.debug('Success Event')
        pass

    def error(self, error):
        self.logger.debug(error.message['message'])
        pass
