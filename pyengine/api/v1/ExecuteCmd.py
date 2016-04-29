import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class ExecuteCmd(Command):

    # Request Parameter Info
    req_params = {
        'server_id': ('r', 'str'),
        'port': ('o', 'str'),
        'user_id': ('o', 'str'),
        'password': ('o', 'str'),
        'id_rsa': ('o', 'str'),
        'id_dsa': ('o', 'str'),
        'cmd': ('r', 'str'),
    }

    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('CloudManager')

        # TODO: Check authentication method
        # one of authentication method is required among password | id_rsa | id_dsa
        # if exist multiple methods, the trying order is password -> id_rsa -> id_dsa

        info = mgr.executeCmd(self.params)

        return info

