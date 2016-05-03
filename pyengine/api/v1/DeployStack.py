import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class DeployStack(Command):

    # Request Parameter Info 
    req_params = {
        'package_id': ('r', 'str'),
        'env': ('o', 'dic'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('PackageManager')

        ctx = {}
        ctx['user_id'] = self.user_meta['user_id']
        ctx['xtoken'] = self.xtoken
        info = mgr.deployStack(self.params, ctx)

        return info.result()
