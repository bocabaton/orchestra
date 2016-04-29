import pytz
from pyengine.lib.error import *
from pyengine.lib.command import Command

class WorkflowTasks(Command):

    # Request Parameter Info 
    req_params = {
        'workflow_id': ('r', 'str'),
        'map': ('o', 'dic'),
        'get': ('o', 'str'),
    }
    
    def __init__(self, api_request):
        super(self.__class__, self).__init__(api_request)

    def execute(self):
        mgr = self.locator.getManager('WorkflowManager')

        if self.params.has_key('map'):
            info = mgr.mapTask(self.params)
        elif self.params.has_key('get'):
            info = mgr.getTaskByName(self.params['workflow_id'], self.params['get'])

        return info.result()
