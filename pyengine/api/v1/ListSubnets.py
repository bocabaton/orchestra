from pyengine.lib.error import *
from pyengine.lib.command import Command

class ListSubnets(Command):

    # Request Parameter Info
    req_params = {
        'vpc_id': ('o', 'str'),
        'name': ('o', 'str'),
        'subnet_id': ('o', 'str'),
        'cidr': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        search = self.makeSearch('vpc_id', 'name', 'subnet_id','cidr') 

        mgr = self.locator.getManager('CloudManager')

        (infos, total_count) = mgr.listSubnets(search)

        response = {}
        response['total_count'] = total_count
        response['results'] = []

        for info in infos:
            response['results'].append(info.result())

        return response
