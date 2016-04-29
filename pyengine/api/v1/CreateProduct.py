import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class CreateProduct(Command):

    # Request Parameter Info 
    req_params = {
        'portfolio_id': ('r', 'str'),
        'name': ('r', 'str'),
        'short_description': ('r', 'str'),
        'description': ('r', 'str'),
        'provided_by': ('r', 'str'),
        'vendor': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('ProductManager')

        info = mgr.createProduct(self.params)

        return info.result()
