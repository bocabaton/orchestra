from pyengine.lib.error import *
from pyengine.lib.command import Command

class GetPortfolio(Command):

    # Request Parameter Info 
    req_params = {
        'portfolio_id': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('PortfolioManager')

        info = mgr.getPortfolio(self.params)

        return info.result()
