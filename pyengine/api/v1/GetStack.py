from pyengine.lib.error import *
from pyengine.lib.command import Command

class GetStack(Command):

    # Request Parameter Info 
    req_params = {
        'stack_id': ('r', 'str'),
        'detail': ('o', 'any'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('PackageManager')

        info = mgr.getStack(self.params)
        result = info.result()
        if self.params.has_key('detail') == True:
            detail = {}
            package_id = info.output['package_id']
            # Get Package Info
            param = {'package_id':package_id}
            mgr = self.locator.getManager('PackageManager')
            package_info = mgr.getPackage(param)
            detail['package'] = package_info.result()
            # Get Product Info
            product_id = package_info.output['product_id']
            param = {'product_id':product_id}
            mgr = self.locator.getManager('ProductManager')
            product_info = mgr.getProduct(param)
            detail['product'] = product_info.result()
            # Get Portfolio Info
            portfolio_id = product_info.output['portfolio_id']
            param = {'portfolio_id':portfolio_id}
            mgr = self.locator.getManager('PortfolioManager')
            portfolio_info = mgr.getPortfolio(param)
            detail['portfolio'] = portfolio_info.result()
            result.update({'detail':detail})

        return result
