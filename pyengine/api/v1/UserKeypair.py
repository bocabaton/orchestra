import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class UserKeypair(Command):

    # Request Parameter Info 
    req_params = {
        'user_id': ('r', 'str'),
        'add': ('o', 'dic'),
        'get': ('o', 'str'),
        'delete': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('UserManager')

        if self.params.has_key('add'):
            info = mgr.addUserKeypair(self.params)
            e_mgr = self.locator.getManager('EventManager')
            e_mgr.addEvent(self.user_meta['user_id'], 'Add User Keypair')

        elif self.params.has_key('get'):
            info = mgr.getUserKeypair(self.params)
        elif self.params.has_key('delete'):
            info = mgr.deleteUserKeypair(self.params)
            return info

        return info
