import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class UserDetail(Command):

    # Request Parameter Info 
    req_params = {
        'user_id': ('r', 'str'),
        'platform': ('r', 'str'),
        'add': ('o', 'dic'),
        'get': ('o', 'str'),
        'update': ('o', 'dic'),
        'delete': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('UserManager')

        if self.params.has_key('add'):
            info = mgr.addUserInfo(self.params)
        elif self.params.has_key('get'):
            info = mgr.getUserInfo(self.params)
        elif self.params.has_key('delete'):
            info = mgr.deleteUserInfo(self.params)
            return info

        return info
