import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class StackEnv(Command):

    # Request Parameter Info 
    req_params = {
        'stack_id': ('r', 'str'),
        'add': ('o', 'dic'),
        'get': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('PackageManager')

        if self.params.has_key('add'):
            info = mgr.addEnv(self.params)
        elif self.params.has_key('get'):
            info = mgr.getEnv2(self.params['stack_id'], self.params['get'])
            return info
        return info.result()
