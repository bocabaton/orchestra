from pyengine.info import VOInfo
from pyengine.lib.error import *

class ZoneInfo(VOInfo):

    def __init__(self, vo, options):
        super(self.__class__, self).__init__(vo, options)

    def __repr__(self):
        return '<ZoneInfo: %s>' %self.vo.zone_id 

    def fetchByVO(self):
        self.output['region_id'] = self.vo.region_id
        self.output['name'] = self.vo.name
        self.output['zone_id'] = self.vo.zone_id
        self.output['zone_type'] = self.vo.zone_type
