from pyengine.info import VOInfo
from pyengine.lib.error import *

class EventInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<EventInfo: %s>' %self.vo.user_id 

    def fetchByVO(self):
        self.output['user_id'] = self.vo.user_id
        self.output['group_id'] = self.vo.group_id
        self.output['msg'] = self.vo.msg
        self.output['created'] = self.vo.created
