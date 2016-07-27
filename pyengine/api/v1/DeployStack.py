import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class DeployStack(Command):

    # Request Parameter Info 
    req_params = {
        'package_id': ('r', 'str'),
        'env': ('o', 'dic'),
        'name': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('PackageManager')

        ctx = {}
        ctx['user_id'] = self.user_meta['user_id']
        ctx['xtoken'] = self.xtoken
        if self.params.has_key('name'):
            ctx['name'] = self.params['name']

        info = mgr.deployStack(self.params, ctx)

        e_mgr = self.locator.getManager('EventManager')
        e_mgr.addEvent(self.user_meta['user_id'], 'DeployStack(%s)' % info.output['stack_id'])

        return info.result()
