from pyengine.lib.error import *
from pyengine.lib.command import Command

class ListStacks(Command):

    # Request Parameter Info
    req_params = {
        #'user_id': ('o', 'str'),
        'state': ('o', 'str'),
        'package': ('o', 'str'),
        #'group_id': ('o', 'str'),
        'detail': ('o','any'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        search = self.makeSearch('package','state') 
        search_or = self.params.get('search_or', [])
        sort = self.params.get('sort', {'key': 'package'})
        page = self.params.get('page', {})

        mgr = self.locator.getManager('PackageManager')

        # TODO: list items of owner only
        (infos, total_count) = mgr.listStacks(search, search_or, sort, page)

        response = {}
        response['total_count'] = total_count
        response['results'] = []

        for info in infos:
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
                # Servers
                cMgr = self.locator.getManager('CloudManager')
                detail['servers'] = cMgr.listServersByStackID(result['stack_id'])
                detail['server_names'] = cMgr.listServerNamesByStackID(result['stack_id'])
                result.update({'detail':detail})
            response['results'].append(result)

        return response
