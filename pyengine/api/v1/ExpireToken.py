from pyengine.lib.error import *
from pyengine.lib.command import Command

class ExpireToken(Command):
    
    # Request Parameter Info
    req_params = {
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        token_mgr = self.locator.getManager('TokenManager')

        result = token_mgr.expireToken(self.params)

        return result
