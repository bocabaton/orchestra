import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class DiscoverCloud(Command):

    # Request Parameter Info 
    req_params = {
        'discover': ('o', 'dic')
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('CloudManager')

        # Find Action type

        # Discovery
        if self.params.has_key('discover'):
            (infos, total_count) = mgr.discoverCloud(self.params)
            response = {}
            response['total_count'] = total_count
            response['results'] = []
            for info in infos:
                response['results'].append(info.result())
            return response


