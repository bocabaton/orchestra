import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class CreatePackage(Command):

    # Request Parameter Info 
    req_params = {
        'product_id': ('r', 'str'),
        'pkg_type': ('o', 'str'),
        'template': ('o', 'str'),
        'version': ('r', 'str'),
        'description': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('PackageManager')

        info = mgr.createPackage(self.params)

        return info.result()
