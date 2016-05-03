from pyengine.lib.error import *
from pyengine.lib.command import Command

class GetUser(Command):

    # Request Parameter Info 
    req_params = {
        'user_id': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        user_mgr = self.locator.getManager('UserManager')

        user_info = user_mgr.getUser(self.params)

        return user_info.result(self.user_meta['timezone'])
