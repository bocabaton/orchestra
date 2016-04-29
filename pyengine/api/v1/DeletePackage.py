from pyengine.lib.error import *
from pyengine.lib.command import Command

class DeletePackage(Command):

    # Request Parameter Info 
    req_params = {
        'package_id': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        # Check Permission

        mgr = self.locator.getManager('PackageManager')

        result = mgr.deletePackage(self.params)

        return result
