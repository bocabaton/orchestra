import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class ServerBrief(Command):

    # Request Parameter Info 
    req_params = {
        'server_id': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('CloudManager')

        info = mgr.getServerBrief(self.params)
        return info
