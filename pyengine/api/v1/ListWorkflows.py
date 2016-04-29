from pyengine.lib.error import *
from pyengine.lib.command import Command

class ListWorkflows(Command):

    # Request Parameter Info
    req_params = {
        'template': ('o', 'str'),
        'template_type': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        search = []
        if self.params.has_key('template'):
            search.add({'template':self.params['template']})
        if self.params.has_key('template_type'):
            search.add({'template_type':self.params['template_type']})

        search_or = self.params.get('search_or', [])
        sort = self.params.get('sort', {'key': 'template_type'})
        page = self.params.get('page', {})

        mgr = self.locator.getManager('ProductManager')

        (infos, total_count) = mgr.listWorkflows(search, search_or, sort, page)

        response = {}
        response['total_count'] = total_count
        response['results'] = []

        for info in infos:
            response['results'].append(info.result())

        return response
