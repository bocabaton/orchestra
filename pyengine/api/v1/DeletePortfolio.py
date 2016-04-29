from pyengine.lib.error import *
from pyengine.lib.command import Command

class DeletePortfolio(Command):

    # Request Parameter Info 
    req_params = {
        'portfolio_id': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        # Check Permission

        mgr = self.locator.getManager('PortfolioManager')

        result = mgr.deletePortfolio(self.params)

        return result
