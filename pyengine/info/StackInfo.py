import json
from pyengine.info import VOInfo
from pyengine.lib.error import *

class StackInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<StackInfo: %s>' %self.vo.stack_id 

    def fetchByVO(self):
        self.output['stack_id'] = self.vo.stack_id
        self.output['package_id'] = self.vo.package_id
        self.output['env'] = json.loads(self.vo.env)
        self.output['state'] = self.vo.state
