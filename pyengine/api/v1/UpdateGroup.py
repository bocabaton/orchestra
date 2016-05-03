from pyengine.lib.error import *
from pyengine.lib.command import Command

class UpdateGroup(Command):

    # Request Parameter Info 
    req_params = {
        'id': ('r', 'str'),
        'name': ('o', 'str'),
        'description': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        group_mgr = self.locator.getManager('GroupManager')

        group_info = group_mgr.updateGroup(self.params)

        return group_info.result(self.user_meta['timezone'])
