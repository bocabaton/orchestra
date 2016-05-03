from pyengine.lib.error import *
from pyengine.lib.command import Command

class ListProducts(Command):

    # Request Parameter Info
    req_params = {
        'name': ('o', 'str'),
        'owner': ('o', 'str'),
        'portfolio_id': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        search = self.makeSearch('name', 'owner', 'portfolio_id') 
        search_or = self.params.get('search_or', [])
        sort = self.params.get('sort', {'key': 'name'})
        page = self.params.get('page', {})

        mgr = self.locator.getManager('ProductManager')

        (infos, total_count) = mgr.listProducts(search, search_or, sort, page)

        response = {}
        response['total_count'] = total_count
        response['results'] = []

        for info in infos:
            response['results'].append(info.result())

        return response
