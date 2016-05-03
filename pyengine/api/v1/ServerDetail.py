import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class ServerDetail(Command):

    # Request Parameter Info 
    req_params = {
        'server_id': ('r', 'str'),
        'get': ('o', 'str'),
        'add': ('o', 'dic'),
        'update': ('o', 'dic'),
        'delete': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('CloudManager')

        if self.params.has_key('add'):
            info = mgr.addServerInfo(self.params)
        elif self.params.has_key('get'):
            info = mgr.getServerInfo2(self.params)
        elif self.params.has_key('delete'):
            info = mgr.deleteServerInfo(self.params)
            return info

        return info
