import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class ActionTag(Command):

    # Request Parameter Info 
    req_params = {
        'product_id': ('r', 'str'),
        'create': ('o', 'dic'),
        'update': ('o', 'dic'),
        'list': ('o', 'list'),
        'delete': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('ProductManager')

        if self.params.has_key('create'):
            info = mgr.createTag(self.params)
        elif self.params.has_key('update'):
            info = mgr.updateTag(self.params)
        elif self.params.has_key('list'):
            search = self.makeSearch('product_id')
            search_or = self.params.get('search_or', [])
            sort = self.params.get('sort',{'key': 'key'})
            page = self.params.get('page', {})

            (infos, total) = mgr.listTags(search, search_or, sort, page)
            # Return Here
            response = {}
            response['total_count'] = total
            response['results'] = []
            for info in infos:
                response['results'].append(info.result())
            return response

        elif self.params.has_key('delete'):
            info = mgr.deleteTag(self.params)
            return info

        return info.result()
