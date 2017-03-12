from pyengine.info import VOInfo
from pyengine.lib.error import *

class SubnetInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<SubnetInfo: %s>' %self.vo.subnet_id 

    def fetchByVO(self):
        self.output['subnet_id'] = self.vo.subnet_id
        self.output['name'] = self.vo.name
        self.output['zone_id'] = self.vo.zone_id
        self.output['vpc_id'] = self.vo.vpc_id
