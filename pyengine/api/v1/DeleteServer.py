from pyengine.lib.error import *
from pyengine.lib.command import Command

class DeleteServer(Command):

    # Request Parameter Info 
    req_params = {
        'server_id': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):

        mgr = self.locator.getManager('CloudManager')

        ctx = {}
        ctx['user_id'] = self.user_meta['user_id']
 
        result = mgr.deleteServer(self.params, ctx)

        e_mgr = self.locator.getManager('EventManager')
        e_mgr.addEvent(self.user_meta['user_id'], 'Delete Server(%s)' % self.params['server_id'])


        return result
