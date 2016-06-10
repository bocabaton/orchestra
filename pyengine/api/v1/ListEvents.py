from pyengine.lib.error import *
from pyengine.lib.command import Command

DEFAULT_LIMIT = 20

class ListEvents(Command):

    # Request Parameter Info
    req_params = {
        'user_id': ('o', 'str'),
        'group_id': ('o', 'str'),
        'limit': ('o', 'int'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        search = self.makeSearch('user_id', 'group_id') 
        search_or = self.params.get('search_or', [])
        sort = self.params.get('sort', {'key': 'created', 'desc':True})
        if self.params.has_key('limit'):
            page = self.params.get('page', {'limit':self.params['limit']})
        else:
            page = self.params.get('page', {'limit':DEFAULT_LIMIT})
        res_params = self.params.get('res_params', [])

        mgr = self.locator.getManager('EventManager')

        (infos, total_count) = mgr.listEvents(search, search_or, sort, page, res_params)

        response = {}
        response['total_count'] = total_count
        response['results'] = []

        for info in infos:
            response['results'].append(info.result(self.user_meta['timezone']))

        return response
