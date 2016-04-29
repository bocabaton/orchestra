import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class UpdatePortfolio(Command):

    # Request Parameter Info 
    req_params = {
        'portfolio_id': ('r', 'str'),
        'name': ('o', 'str'),
        'description': ('o', 'str'),
        'owner': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('PortfolioManager')

        info = mgr.updatePortfolio(self.params)

        return info.result()
