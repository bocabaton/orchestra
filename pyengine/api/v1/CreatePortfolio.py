import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class CreatePortfolio(Command):

    # Request Parameter Info 
    req_params = {
        'name': ('r', 'str'),
        'description': ('o', 'str'),
        'owner': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('PortfolioManager')

        info = mgr.createPortfolio(self.params)

        return info.result()
