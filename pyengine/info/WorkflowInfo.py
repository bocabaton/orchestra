from pyengine.info import VOInfo
from pyengine.lib.error import *

class WorkflowInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<WorkflowInfo: %s>' %self.vo.workflow_id

    def fetchByVO(self):
        self.output['workflow_id'] = self.vo.workflow_id
        self.output['template'] = self.vo.template
        self.output['template_type'] = self.vo.template_type
