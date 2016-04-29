from pyengine.info import VOInfo
from pyengine.lib.error import *

class RegionInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<RegionInfo: %s>' %self.vo.region_id 

    def fetchByVO(self):
        self.output['region_id'] = self.vo.region_id
        self.output['name'] = self.vo.name
