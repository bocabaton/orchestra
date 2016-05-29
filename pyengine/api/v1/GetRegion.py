from pyengine.lib.error import *
from pyengine.lib.command import Command

class GetRegion(Command):

    # Request Parameter Info 
    req_params = {
        'region_id': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('CloudManager')

        info = mgr.getRegion(self.params)

        return info.result()
