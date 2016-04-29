import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class UpdateProduct(Command):

    # Request Parameter Info 
    req_params = {
        'product_id': ('r', 'str'),
        'name': ('o', 'str'),
        'short_description': ('o', 'str'),
        'description': ('o', 'str'),
        'provided_by': ('o', 'str'),
        'vendor': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('ProductManager')

        info = mgr.updateProduct(self.params)

        return info.result()
