import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class ZoneDetail(Command):

    # Request Parameter Info 
    req_params = {
        'create': ('o', 'dic'),
        'get': ('o', 'str'),
        'delete': ('o', 'str')
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('CloudManager')

        if self.params.has_key('create'):
            info = mgr.CreateZoneDetail(self.params['create'])
        
        return info.result()
