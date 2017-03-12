from pyengine.info import VOInfo
from pyengine.lib.error import *

class VpcInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<VpcInfo: %s>' %self.vo.vpc_id 

    def fetchByVO(self):
        self.output['vpc_id'] = self.vo.vpc_id
        self.output['name'] = self.vo.name
