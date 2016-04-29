import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class CreateServer(Command):

    # Request Parameter Info 
    req_params = {
        'name': ('r', 'str'),
        'zone_id': ('r', 'str'),
        'floatingIP': ('o', 'bool'),
        'request': ('r', 'dic'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('CloudManager')

        info = mgr.createServer(self.params)
        return info.result()
