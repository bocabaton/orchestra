from pyengine.lib.error import *
from pyengine.lib.command import Command

class GetPackage(Command):

    # Request Parameter Info 
    req_params = {
        'package_id': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('PackageManager')

        info = mgr.getPackage(self.params)

        return info.result()
