from pyengine.lib.error import *
from pyengine.lib.command import Command

class ListGroups(Command):

    # Request Parameter Info
    req_params = {
        'id': ('o', 'str'),
        'search': ('o', 'list'),
        'search_or': ('o', 'list'),
        'sort': ('o', 'dic'),
        'page': ('o', 'dic'),
        'res_params': ('o', 'list'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        if self.params.has_key('id'):
            self.params['uuid'] = self.params['id']

        search = self.makeSearch('uuid') 
        search_or = self.params.get('search_or', [])
        sort = self.params.get('sort', {'key': 'uuid'})
        page = self.params.get('page', {})
        res_params = self.params.get('res_params', [])

        group_mgr = self.locator.getManager('GroupManager')

        (group_infos, total_count) = group_mgr.listGroups(search, search_or, sort, page, res_params)

        response = {}
        response['total_count'] = total_count
        response['results'] = []

        for group_info in group_infos:
            response['results'].append(group_info.result(self.user_meta['timezone']))

        return response
