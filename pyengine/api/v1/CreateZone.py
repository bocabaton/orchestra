import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class CreateZone(Command):

    # Request Parameter Info 
    req_params = {
        'name': ('r', 'str'),
        'region_id': ('r', 'str'),
        'zone_type': ('r', 'str')
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('CloudManager')

        info = mgr.createZone(self.params)
        
        return info.result()
