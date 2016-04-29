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

        info = mgr.deployStack(self.params)

        return info.result()
