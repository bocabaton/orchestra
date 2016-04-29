import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class UpdatePackage(Command):

    # Request Parameter Info 
    req_params = {
        'package_id': ('r', 'str'),
        'pkg_type': ('o', 'str'),
        'template': ('o', 'str'),
        'version': ('o', 'str'),
        'description': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('PackageManager')

        info = mgr.updatePackage(self.params)

        return info.result()
