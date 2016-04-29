import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class RegisterWorkflow(Command):

    # Request Parameter Info 
    req_params = {
        'template': ('r', 'str'),
        'template_type': ('r', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('WorkflowManager')

        info = mgr.registerWorkflow(self.params)

        return info.result()
