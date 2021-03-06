from pyengine.lib.error import *
from pyengine.lib.command import Command

class ListRegions(Command):

    # Request Parameter Info
    req_params = {
        'region_id': ('o', 'str'),
        'name': ('o', 'str'),
        'brief': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        search = self.makeSearch('region_id', 'name') 

        mgr = self.locator.getManager('CloudManager')

        if self.params.has_key('brief') == True:
            brief = True
        else:
            brief = False

        (infos, total_count) = mgr.listRegions(search, brief)

        response = {}
        response['total_count'] = total_count
        response['results'] = []

        for info in infos:
            response['results'].append(info.result())

        return response
