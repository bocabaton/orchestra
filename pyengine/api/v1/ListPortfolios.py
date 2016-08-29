from pyengine.lib.error import *
from pyengine.lib.command import Command

class ListPortfolios(Command):

    # Request Parameter Info
    req_params = {
        'name': ('o', 'str'),
        'owner': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        search = self.makeSearch('name', 'owner') 
        search_or = self.params.get('search_or', [])
        sort = self.params.get('sort', {'key': 'name'})
        page = self.params.get('page', {})

        mgr = self.locator.getManager('PortfolioManager')

        (infos, total_count) = mgr.listPortfolios(search, search_or, sort, page)

        response = {}
        response['total_count'] = total_count
        response['results'] = []

        for info in infos:
            response['results'].append(info.result())

        return response
