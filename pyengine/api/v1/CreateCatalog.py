import os
import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class CreateCatalog(Command):

    # Request Parameter Info 
    req_params = {
        'url': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        cmd = "jeju -m %s -L /tmp/catalog.log" % self.params['url']
        self.logger.debug(cmd)
        os.system(cmd)

        return {'success': 'ok'}
