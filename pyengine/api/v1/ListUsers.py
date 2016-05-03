from pyengine.lib.error import *
from pyengine.lib.command import Command

class ListUsers(Command):

    # Request Parameter Info
    req_params = {
        'user_id': ('o', 'str'),
        'state': ('o', 'str'),
        'group_id': ('o', 'str'),
        'search': ('o', 'list'),
        'search_or': ('o', 'list'),
        'sort': ('o', 'dic'),
        'page': ('o', 'dic'),
        'res_params': ('o', 'list'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        search = self.makeSearch('user_id', 'state', 'group_id') 
        search_or = self.params.get('search_or', [])
        sort = self.params.get('sort', {'key': 'user_id'})
        page = self.params.get('page', {})
        res_params = self.params.get('res_params', [])

        user_mgr = self.locator.getManager('UserManager')

        (user_infos, total_count) = user_mgr.listUsers(search, search_or, sort, page, res_params)

        response = {}
        response['total_count'] = total_count
        response['results'] = []

        for user_info in user_infos:
            response['results'].append(user_info.result(self.user_meta['timezone']))

        return response
