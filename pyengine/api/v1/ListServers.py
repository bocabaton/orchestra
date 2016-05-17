from pyengine.lib.error import *
from pyengine.lib.command import Command

class ListServers(Command):

    # Request Parameter Info
    req_params = {
        'server_id': ('o', 'str'),
        'name': ('o', 'str'),
        'zone_id': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        search = self.makeSearch('server_id', 'name', 'zone_id') 

        mgr = self.locator.getManager('CloudManager')

        (infos, total_count) = mgr.listServers(search)

        response = {}
        response['total_count'] = total_count
        response['results'] = []

        for info in infos:
            response['results'].append(info.result())

        return response
