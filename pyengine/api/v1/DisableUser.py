from pyengine.lib.error import *
from pyengine.lib.command import Command

class DisableUser(Command):

    # Request Parameter Info 
    req_params = {
        'user_id': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        if self.params['user_id'] in [self.user_meta['user_id'], 'root']:
            raise ERROR_NO_PERMISSIONS()

        user_mgr = self.locator.getManager('UserManager')

        user_info = user_mgr.disableUser(self.params)

        return user_info.result(self.user_meta['timezone'])
