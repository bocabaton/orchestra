from pyengine.lib.error import *
from pyengine.lib.command import Command

class ListPackages(Command):

    # Request Parameter Info
    req_params = {
        'product_id': ('o', 'str'),
        'search_or': ('o', 'list'),
        'sort': ('o', 'dic'),
        'page': ('o', 'dic'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        if self.params.has_key('product_id'):
            search = [{'key':'product', 'value':self.params['product_id'], 'option':'eq'}]
        #search = self.makeSearch('product_id') 
        search_or = self.params.get('search_or', [])
        sort = self.params.get('sort', {'key': 'product_id'})
        page = self.params.get('page', {})

        mgr = self.locator.getManager('PackageManager')

        (infos, total_count) = mgr.listPackages(search, search_or, sort, page)

        response = {}
        response['total_count'] = total_count
        response['results'] = []

        for info in infos:
            response['results'].append(info.result())

        return response
