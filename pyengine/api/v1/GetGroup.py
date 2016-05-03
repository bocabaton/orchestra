from pyengine.lib.error import *
from pyengine.lib.command import Command

class GetGroup(Command):

    # Request Parameter Info 
    req_params = {
        'id': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        group_mgr = self.locator.getManager('GroupManager')

        group_info = group_mgr.getUser(self.params)

        return group_info.result(self.user_meta['timezone'])
