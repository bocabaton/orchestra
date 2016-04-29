from pyengine.info import VOInfo
from pyengine.lib.error import *

class TaskInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<TaskInfo: %s>' %self.vo.task_id

    def fetchByVO(self):
        self.output['task_id'] = self.vo.task_id
        self.output['name'] = self.vo.name
        self.output['workflow_id'] = self.vo.workflow_id
        self.output['task_uri'] = self.vo.task_uri
        self.output['task_type'] = self.vo.task_type
